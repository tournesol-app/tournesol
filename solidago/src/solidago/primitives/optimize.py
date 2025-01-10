"""
A jitted version of `scipy.optimize.brentq` to be used with Numba.
Adapted from QuantEcon.py
https://github.com/QuantEcon/QuantEcon.py/blob/v0.7.0/quantecon/optimize/root_finding.py

Copyright © 2013-2021 Thomas J. Sargent and John Stachurski: BSD-3
All rights reserved.
"""

from typing import Callable, Tuple, Literal, Optional, Any
from functools import cache

import numpy as np
from numba import njit


_ECONVERGED = 0
_ECONVERR = -1

_iter = 100
_xtol = 2e-12
_rtol = 4 * np.finfo(float).eps


# @njit
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


# @njit
def njit_brentq(
    f,
    args=(),
    xtol=_xtol,
    rtol=_rtol,
    maxiter=_iter,
    a: float=-1.0,
    b: float=1.0,
    extend_bounds: bool=True,
    xmin: float = -1e30,
    xmax: float = 1e30,
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
    if extend_bounds:
        fa = f(a, *args) 
        fb = f(b, *args)
        while (a > xmin or b < xmax) and (fa * fb > 0):
            a = max(a - 2 * (b - a), xmin)
            b = min(b + 2 * (b - a), xmax)
            fa = f(a, *args) 
            fb = f(b, *args)

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


def coordinate_updates(
    update_coordinate_function: Callable[[int, np.ndarray, Tuple], float],
    get_update_coordinate_function_args: Callable[[int, np.ndarray], Tuple],
    initialization: np.ndarray,
    updated_coordinates: Optional[list[int]]=None,
    error: float=1e-5,
    max_iter: int=10000,
):
    """Minimize a loss function with coordinate descent,
    by leveraging the partial derivatives of the loss

    Parameters
    ----------
    update_coordinate_function: callable
        (int: coordinate, variable: np.ndarray, args: tuple) -> float
        Returns the updated value on 'coordinate', given a current 'variable', 
        with additional arguments args.
    get_update_coordinate_function_args: callable
        (coordinate: int, variable: np.ndarray) -> (coordinate_update_args: tuple)
        Return the 'args' of update_coordinate_function
    initialization: np.array
        Initialization point of the coordinate descent
    error: float
        Tolerated error
    max_iter: int
        Maximum number of iterations

    Returns
    -------
    out: stationary point of the loss
        For well behaved losses, there is a convergence guarantee
    """
    unchanged = set()
    to_pick = list() if updated_coordinates is None else updated_coordinates
    variable = initialization
    variable_len = len(variable)
    iteration_number = 0

    def pick_next_coordinate():
        nonlocal to_pick
        if not to_pick:
            to_pick = list(range(variable_len))
            np.random.shuffle(to_pick)
        return to_pick.pop()

    while len(unchanged) < variable_len and iteration_number < max_iter:
        iteration_number += 1
        coordinate = pick_next_coordinate()
        if coordinate in unchanged:
            continue
        old_coordinate_value = variable[coordinate]
        args = get_update_coordinate_function_args(coordinate, variable)
        new_coordinate_value = update_coordinate_function(coordinate, variable, *args)
        variable[coordinate] = new_coordinate_value
        if abs(new_coordinate_value - old_coordinate_value) < error:
            unchanged.add(coordinate)
        else:
            unchanged.clear()
    return variable


def coordinate_descent(
    partial_derivative: Callable[[int, np.ndarray[np.float64], Tuple], float],
    initialization: np.ndarray,
    get_partial_derivative_args: Optional[Callable[[int, np.ndarray[np.float64], Tuple], Tuple]]=None,
    get_update_coordinate_function_args: Optional[Callable[[int, np.ndarray[np.float64]], Tuple]]=None,
    updated_coordinates: Optional[list[int]]=None,
    error: float=1e-5,
    coordinate_optimization_xtol: float=1e-5
):
    """Minimize a loss function with coordinate descent,
    by leveraging the partial derivatives of the loss

    Parameters
    ----------
    partial_derivative: jitted callable
        (x: float, partial_derivative_args: Tuple) -> float
        Returns the partial derivative of the loss to optimize
    get_partial_derivative_args: jitted callable(
            coordinate: int, 
            variable: np.ndarray, 
            coordinate_update_args: Tuple
        ) -> (partial_derivative_args: Tuple)
        retrieves the arguments needed to optimize `variable` along `coordinate`
    get_update_coordinate_function_args: callable
        (coordinate: int, variable: np.ndarray) -> (coordinate_update_args: tuple)
        Return the 'args' of update_coordinate_function
    initialization: np.array
        Initialization point of the coordinate descent
    error: float
        Tolerated error
    coordinate_optimization_xtol: float
        Tolerated error in brentq's coordinate update

    Returns
    -------
    out: stationary point of the loss
        For well behaved losses, there is a convergence guarantee
    """
    # First define the update_coordinate_function associated to coordinatewise descent
    # by leveraging njit and brentq
    
    empty_function = lambda coordinate, variable: tuple()
    
    if get_partial_derivative_args is None:
        get_partial_derivative_args = empty_function
        
    if get_update_coordinate_function_args is None:
        get_update_coordinate_function_args = empty_function

    def coordinate_function(
        coordinate: int, 
        variable: np.ndarray[np.float64],
    ) -> Callable[[float, Tuple], float]:
        # @njit
        def f(value: np.float64, *partial_derivative_args) -> np.float64:
            return partial_derivative(coordinate, np.array([ 
                variable[i] if i != coordinate else value
                for i in range(len(variable))
            ], dtype=np.float64), *partial_derivative_args)
        return f
    
    def update_coordinate_function(
        coordinate: int, 
        variable: np.ndarray[np.float64], 
        *coordinate_update_args
    ) -> float:
        return njit_brentq(
            f=coordinate_function(coordinate, variable),
            args=get_partial_derivative_args(coordinate, variable, *coordinate_update_args),
            xtol=coordinate_optimization_xtol,
            a=variable[coordinate] - 1.0,
            b=variable[coordinate] + 1.0
        )
        
    return coordinate_updates(
        update_coordinate_function=update_coordinate_function,
        get_update_coordinate_function_args=get_update_coordinate_function_args,
        initialization=initialization,
        updated_coordinates=updated_coordinates,
        error=error,
    )
