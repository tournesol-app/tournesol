import pytest
import numpy as np

from numba import njit

from solidago.primitives.dichotomy import solve as dichotomy_solve
from solidago.primitives.optimize import njit_brentq as brentq
from solidago.primitives.optimize import coordinate_updates, coordinate_descent


def test_dichotomy():
    assert dichotomy_solve(lambda t: t, 1, 0, 3) == pytest.approx(1, abs=1e-4)
    assert dichotomy_solve(lambda t: 2 - t**2, 1, 0, 3) == pytest.approx(1, abs=1e-4)


def test_brentq_fails_to_converge_for_non_zero_method():
    @njit
    def one_plus_x_square(x):
        return 1 + x * x

    with pytest.raises(ValueError):
        brentq(one_plus_x_square, extend_bounds=False)


def test_brentq_finds_zeros_of_simple_increasing_linear():
    @njit
    def x_plus_five(x):
        return x + 5

    assert brentq(x_plus_five) == -5.0


def test_brentq_finds_zeros_of_simple_decreasing_linear():
    @njit
    def minus_x_plus_twelve(x):
        return -x + 12

    assert brentq(minus_x_plus_twelve) == 12.0


def test_update_coordinates():
    @njit
    def update_coordinate_function(coordinate: int, variable: np.ndarray, *args) -> float:
        if coordinate == 0:
            return 0
        elif variable[coordinate - 1] == 0:
            return 0
        return variable[coordinate]
    
    @njit
    def get_update_coordinate_function_args(coordinate: int, variable: np.ndarray) -> tuple:
        return tuple()

    result = coordinate_updates(
        update_coordinate_function,
        get_update_coordinate_function_args,
        initialization=np.array([1, 4, 3, 2, 1])
    )
    assert all({ result[i] == 0 for i in range(5) })


def test_brentq_on_partial_derivative():
    @njit
    def partial_derivative(coordinate: int, variable: np.ndarray, *args) -> float:
        if args != (1, 2):
            raise ValueError(args)
        return (coordinate + 1.0) * variable[coordinate]

    @njit
    def get_partial_derivative_args(coordinate: int, variable: np.ndarray, *args) -> tuple: 
        return (1, 2)
    
    def coordinate_function(coordinate: int, variable: np.ndarray):
        @njit
        def njit_partial_derivative(value: float, *args) -> float:
            if args[0] != 1:
                raise ValueError(args)
            return partial_derivative(coordinate, np.array([ 
                variable[i] if i != coordinate else value
                for i in range(len(variable))
            ], dtype=np.float64), *args)
        return njit_partial_derivative

    coordinate = 2
    variable = np.arange(5, dtype=np.float64)
    x = brentq(
        f=coordinate_function(coordinate, variable),
        args=get_partial_derivative_args(coordinate, variable)
    )
    assert x == 0.0


def test_coordinate_descent():
    @njit
    def partial_derivative(coordinate: int, variable: np.ndarray, *args) -> float:
        if args != (1, 2):
            raise ValueError(args)
        if coordinate == 0:
            return variable[coordinate]
        return (coordinate + 1) * (variable[coordinate] + coordinate + variable[coordinate - 1])
    
    @njit
    def get_partial_derivative_args(coordinate: int, variable: np.ndarray, *args) -> tuple: 
        if len(args) > 0 and args != (0, 8, 4):
            raise ValueError(args)
        return (1, 2)
    
    @njit
    def get_update_coordinate_function_args(coordinate: int, variable: np.ndarray) -> tuple:
        return (0, 8, 4)
    
    result = coordinate_descent(
        partial_derivative,
        np.arange(10),
        get_partial_derivative_args,
        get_update_coordinate_function_args,
    )
    result2 = coordinate_descent(
        partial_derivative,
        np.arange(10),
        get_partial_derivative_args,
    ) 
    assert list(result) == list(result2)
    assert list(result) == [0, -1, -1, -2, -2, -3 , -3, -4, -4, -5]
