import pytest

from numba import njit

from solidago.solvers.optimize import brentq


def test_brentq_fails_to_converge_for_non_zero_method():
    @njit
    def one_plus_x_square(x):
        return 1 + x * x
    with pytest.raises(RuntimeError):
        brentq(one_plus_x_square)


def test_brentq_finds_zeros_of_simple_increasing_linear():
    @njit
    def x_plus_five(x):
        return x+5
    assert brentq(x_plus_five) == -5.


def test_brentq_finds_zeros_of_simple_decreasing_linear():
    @njit
    def minus_x_plus_twelve(x):
        return -x+12
    assert brentq(minus_x_plus_twelve) == 12.
