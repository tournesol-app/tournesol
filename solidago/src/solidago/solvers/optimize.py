"""
A jitted version of `scipy.optimize.brentq` to be used with Numba.
Adapted from QuantEcon.py
https://github.com/QuantEcon/QuantEcon.py/blob/v0.7.0/quantecon/optimize/root_finding.py

Copyright © 2013-2021 Thomas J. Sargent and John Stachurski: BSD-3
All rights reserved.
"""
# pylint: skip-file
from typing import Tuple, Callable, Optional

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

class SignChangeIntervalNotFoundError(RuntimeError):
    pass

@njit
def search_sign_change_interval(
    f: Callable,
    a: float,
    b: float,
    args: Tuple = (),
    max_iterations: int = 32,
    search_a: bool = True,
    search_b: bool = True,
):
    """
        Searches bounds a and b of interval where `f` changes sign. This is
        achieved by increasing the size of the interval iteratively.
        Note that the method is not guaranteed to succeed for most functions
        and highly depends on the initial bounds.

        Parameters
        ----------
        f : jitted and callable
            Python function returning a number.  `f` must be continuous.
        a : number
            One end of the bracketing interval [a,b].
        b : number
            The other end of the bracketing interval [a,b].
        args : tuple, optional(default=())
            Extra arguments to be used in the function call.
        max_iterations:
            The maximum number of iteration in the search. /!\ When using a
            large number of iterations, bounds would become very large and
            functions may not be well behaved.
        search_a:
            If true, the value of `a` provided will be updated to search for an
            interval where `f` changes sign
        search_b:
            If true, the value of `b` provided will be updated to search for an
            interval where `f` changes sign

        Returns
        -------
        a, b:
            An interval on which the continuous function `f` changes sign
    """
    if a >= b:
        raise ValueError(f"Initial interval bounds should be such that a < b. Found a={a} and b={b}")
    iteration_count = 0
    while f(a, *args) * f(b, *args) > 0:
        if iteration_count > max_iterations:
            raise SignChangeIntervalNotFoundError("Could not find a sign changing interval")
        iteration_count+=1
        a = a-(b-a) if search_a else a
        b = b+(b-a) if search_b else b
    return a, b

@njit
def brentq(f, args=(), xtol=_xtol, rtol=_rtol, maxiter=_iter, disp=True, a: float=-1.0, b: float=1.0, search_a: bool=True, search_b: bool = True) -> float:
    """
    Find a root of a function in a bracketing interval using Brent's method
    adapted from Scipy's brentq.
    Uses the classic Brent's method to find a zero of the function `f` on
    the sign changing interval [a , b].
    `f` must be jitted via numba.
    Parameters
    ----------
    f : jitted and callable
        Python function returning a number.  `f` must be continuous.
    a : number
        One end of the bracketing interval [a,b].
    b : number
        The other end of the bracketing interval [a,b].
    args : tuple, optional(default=())
        Extra arguments to be used in the function call.
    xtol : number, optional(default=2e-12)
        The computed root ``x0`` will satisfy ``np.allclose(x, x0,
        atol=xtol, rtol=rtol)``, where ``x`` is the exact root. The
        parameter must be nonnegative.
    rtol : number, optional(default=4*np.finfo(float).eps)
        The computed root ``x0`` will satisfy ``np.allclose(x, x0,
        atol=xtol, rtol=rtol)``, where ``x`` is the exact root.
    maxiter : number, optional(default=100)
        Maximum number of iterations.
    disp : bool, optional(default=True)
        If True, raise a RuntimeError if the algorithm didn't converge.
    search_a:
        If true, the value of `a` provided will be updated to search for an
        interval where `f` changes sign
    search_b:
        If true, the value of `b` provided will be updated to search for an
        interval where `f` changes sign
    Returns
    -------
    root : float
    """
    a, b = search_sign_change_interval(f, a, b, args=args, search_a=search_a, search_b=search_b)
    if f(a, *args) == 0:
        return a
    if f(b, *args) == 0:
        return b
    if f(a, *args) * f(b, *args) > 0:
        raise ValueError("Function `f` should have opposite sign on bounds `a` and `b`")

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

    if disp and status == _ECONVERR:
        raise RuntimeError("Failed to converge")

    return root  # type: ignore
