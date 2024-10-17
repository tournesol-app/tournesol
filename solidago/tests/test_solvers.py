import pytest
from numba import njit

from solidago.solvers.dichotomy import solve as dichotomy_solve
from solidago.solvers.optimize import njit_brentq as brentq


def test_dichotomy():
    assert dichotomy_solve(lambda t: t, 1, 0, 3) == pytest.approx(1, abs=1e-4)
    assert dichotomy_solve(lambda t: 2 - t**2, 1, 0, 3) == pytest.approx(1, abs=1e-4)


def test_brentq_fails_to_converge_for_non_zero_method():
    @njit
    def one_plus_x_square(x):
        return 1 + x * x

    with pytest.raises(ValueError):
        brentq(one_plus_x_square, extend_bounds="no")


def test_brentq_finds_zeros_of_simple_increasing_linear():
    @njit
    def x_plus_five(x):
        return x + 5

    assert brentq(x_plus_five, extend_bounds="ascending") == -5.0


def test_brentq_finds_zeros_of_simple_decreasing_linear():
    @njit
    def minus_x_plus_twelve(x):
        return -x + 12

    assert brentq(minus_x_plus_twelve, extend_bounds="descending") == 12.0
