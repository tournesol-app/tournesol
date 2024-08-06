"""
A jitted version of `scipy.optimize.brentq` to be used with Numba.
Adapted from QuantEcon.py
https://github.com/QuantEcon/QuantEcon.py/blob/v0.7.0/quantecon/optimize/root_finding.py

Copyright © 2013-2021 Thomas J. Sargent and John Stachurski: BSD-3
All rights reserved.
"""

from typing import Callable, Tuple, Literal

import numpy as np
from numba import njit


_ECONVERGED = 0
_ECONVERR = -1

_iter = 100
_xtol = 2e-12
_rtol = 4 * np.finfo(float).eps


@njit
def _bisect_interval(a, b, fa, fb) -> Tuple[float, int]:
    """Conditional checks for intervals in methods involving bisection"""
    if fa * fb > 0:
        raise ValueError("f(a) and f(b) must have different signs")
    root = 0.0
    status = _ECONVERR

    # Root found at either end of [a,b]
    if fa == 0:
        root = a
        status = _ECONVERGED
    if fb == 0:
        root = b
        status = _ECONVERGED

    return root, status


@njit
def njit_brentq(
    f,
    args=(),
    xtol=_xtol,
    rtol=_rtol,
    maxiter=_iter,
    a: float = -1.0,
    b: float = 1.0,
    extend_bounds: Literal["ascending", "descending", "no"] = "ascending",
) -> float:
    """Accelerated brentq. Requires f to be itself jitted via numba.
    Essentially, numba optimizes the execution by running an optimized compilation
    of the function when it is first called, and by then running the compiled function.

    Parameters
    ----------
    f : jitted and callable
        Python function returning a number.  `f` must be continuous.
    args : tuple, optional(default=())
        Extra arguments to be used in the function call.
    xtol : number, optional(default=2e-12)
        The computed root ``x0`` will satisfy ``np.allclose(x, x0,
        atol=xtol, rtol=rtol)``, where ``x`` is the exact root. The
        parameter must be nonnegative.
    rtol : number, optional(default=`4*np.finfo(float).eps`)
        The computed root ``x0`` will satisfy ``np.allclose(x, x0,
        atol=xtol, rtol=rtol)``, where ``x`` is the exact root.
    maxiter : number, optional(default=100)
        Maximum number of iterations.
    a : number
        One end of the bracketing interval [a,b].
    b : number
        The other end of the bracketing interval [a,b].
    extend_bounds: default: "ascending",
        Whether to extend the interval [a,b] to find a root.
        ('no': to keep the bounds [a, b],
        'ascending': extend the bounds assuming `f` is ascending,
        'descending': extend the bounds assuming `f` is descending)
    """
    if extend_bounds == "ascending":
        while f(a, *args) > 0:
            a = a - 2 * (b - a)
        while f(b, *args) < 0:
            b = b + 2 * (b - a)
    elif extend_bounds == "descending":
        while f(a, *args) < 0:
            a = a - 2 * (b - a)
        while f(b, *args) > 0:
            b = b + 2 * (b - a)

    if xtol <= 0:
        raise ValueError("xtol is too small (<= 0)")
    if maxiter < 1:
        raise ValueError("maxiter must be greater than 0")

    # Convert to float
    xpre = a * 1.0
    xcur = b * 1.0

    fpre = f(xpre, *args)
    fcur = f(xcur, *args)
    funcalls = 2

    root, status = _bisect_interval(xpre, xcur, fpre, fcur)

    # Check for sign error and early termination
    if status == _ECONVERGED:
        itr = 0
    else:
        # Perform Brent's method
        for itr in range(maxiter):

            if fpre * fcur < 0:
                xblk = xpre
                fblk = fpre
                spre = scur = xcur - xpre
            if abs(fblk) < abs(fcur):
                xpre = xcur
                xcur = xblk
                xblk = xpre

                fpre = fcur
                fcur = fblk
                fblk = fpre

            delta = (xtol + rtol * abs(xcur)) / 2
            sbis = (xblk - xcur) / 2

            # Root found
            if fcur == 0 or abs(sbis) < delta:
                status = _ECONVERGED
                root = xcur
                itr += 1
                break

            if abs(spre) > delta and abs(fcur) < abs(fpre):
                if xpre == xblk:
                    # interpolate
                    stry = -fcur * (xcur - xpre) / (fcur - fpre)
                else:
                    # extrapolate
                    dpre = (fpre - fcur) / (xpre - xcur)
                    dblk = (fblk - fcur) / (xblk - xcur)
                    stry = -fcur * (fblk * dblk - fpre * dpre) / (dblk * dpre * (fblk - fpre))

                if 2 * abs(stry) < min(abs(spre), 3 * abs(sbis) - delta):
                    # good short step
                    spre = scur
                    scur = stry
                else:
                    # bisect
                    spre = sbis
                    scur = sbis
            else:
                # bisect
                spre = sbis
                scur = sbis

            xpre = xcur
            fpre = fcur
            if abs(scur) > delta:
                xcur += scur
            else:
                xcur += delta if sbis > 0 else -delta
            fcur = f(xcur, *args)
            funcalls += 1

    if status == _ECONVERR:
        raise RuntimeError("Failed to converge")

    return root  # type: ignore


def coordinate_descent(
    update_coordinate_function: Callable[[Tuple, float], float],
    get_args: Callable[[int, np.ndarray], Tuple],
    initialization: np.ndarray,
    updated_coordinates: list[int],
    error: float = 1e-5,
):
    """Minimize a loss function with coordinate descent,
    by leveraging the partial derivatives of the loss

    Parameters
    ----------
    loss_partial_derivative: callable
        (coordinate: int, coordinate_value: float, solution: np.array) -> float
        Returns the partial derivative of a loss, along coordinate,
        when the coordinate value is modified
    initialization: np.array
        Initialization point of the coordinate descent
    error: float
        Tolerated error

    Returns
    -------
    out: stationary point of the loss
        For well behaved losses, there is a convergence guarantee
    """
    unchanged = set()
    to_pick = updated_coordinates
    solution = initialization
    solution_len = len(solution)

    def pick_next_coordinate():
        nonlocal to_pick
        if not to_pick:
            to_pick = list(range(solution_len))
            np.random.shuffle(to_pick)
        return to_pick.pop()

    while len(unchanged) < solution_len:
        coordinate = pick_next_coordinate()
        if coordinate in unchanged:
            continue
        old_coordinate_value = solution[coordinate]
        new_coordinate_value = update_coordinate_function(
            get_args(coordinate, solution),
            old_coordinate_value,
        )
        solution[coordinate] = new_coordinate_value
        if abs(new_coordinate_value - old_coordinate_value) < error:
            unchanged.add(coordinate)
        else:
            unchanged.clear()
    return solution
