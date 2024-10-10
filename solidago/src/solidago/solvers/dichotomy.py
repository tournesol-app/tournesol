from typing import Callable

import numpy as np


def solve(
    f: Callable[..., float],
    value: float = 0,
    xmin: float = 0,
    xmax: float = 1,
    error: float = 1e-6,
    args = (),
):
    """Solves for f(x) == value, using dichotomy search
    May return an error if f(xmin) * f(xmax) > 0

    Parameters
    ----------
    f: callable
        f must be a function f(x:float) -> float
    value: float
        The value to invert
    xmin: float
    xmax: float
        A solution is searched in the interval [xmin, xmax]
    error: float
        Terminates if |xmin - xmax| < error

    Returns
    -------
    out: float
    """
    ymin, ymax = f(xmin, *args) - value, f(xmax, *args) - value
    if ymin * ymax > 0:
        raise ValueError(f"No solution to f(x)={value} was found in [{xmin}, {xmax}]")

    delta = np.abs(xmax - xmin)
    if delta <= error:
        return (xmin + xmax) / 2

    n_iterations = int(np.ceil(np.log2(delta / error)))
    for _ in range(n_iterations):
        x = (xmin + xmax) / 2
        y = f(x, *args) - value
        if y == 0:
            return x
        if ymin * y < 0:
            xmax = x
        else:
            xmin = x

    return (xmin + xmax) / 2
