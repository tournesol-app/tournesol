from typing import Any, Callable
from numpy.typing import NDArray
from solidago.primitives.minimizer.minimizer import Minimizer

import numpy as np

from solidago.primitives.minimizer.brentq import njit_brentq


def empty_function(_coordinate: int, _variable: NDArray[np.float64], *args: Any) -> tuple[Any, ...]:
    return ()


class CoordinateDescent(Minimizer):
    def __init__(self, convergence_error: float=1e-5, max_iter: int=1000):
        self.convergence_error = convergence_error
        self.max_iter = max_iter

    def updates(self,
        update_coordinate_function: Callable[[int, NDArray[np.float64], tuple[Any, ...]], float],
        initialization: NDArray[np.float64],
        get_update_coordinate_function_args: Callable[[int, NDArray[np.float64]], tuple[Any, ...]] | None = None,
        updated_coordinates: list[int] | None = None,
    ) -> NDArray[np.float64]:
        """Minimize a loss function with coordinate descent,
        by leveraging the partial derivatives of the loss

        Parameters
        ----------
        update_coordinate_function: callable
            (int: coordinate, variable: NDArray, args: tuple) -> float
            Returns the updated value on 'coordinate', given a current 'variable', 
            with additional arguments args.
        get_update_coordinate_function_args: callable
            (coordinate: int, variable: NDArray) -> (coordinate_update_args: tuple)
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
        if get_update_coordinate_function_args is None:
            get_update_coordinate_function_args = lambda coordinate, variable: ()

        unchanged: set[int] = set()
        to_pick: list[int] = list() if updated_coordinates is None else updated_coordinates
        variable = initialization
        variable_len = len(variable)
        iteration_number = 0

        def pick_next_coordinate():
            nonlocal to_pick
            if not to_pick:
                to_pick = list(range(variable_len))
                np.random.shuffle(to_pick)
            return to_pick.pop()

        while len(unchanged) < variable_len and iteration_number < self.max_iter:
            iteration_number += 1
            coordinate = pick_next_coordinate()
            if coordinate in unchanged:
                continue
            old_coordinate_value = variable[coordinate]
            args = get_update_coordinate_function_args(coordinate, variable)
            new_coordinate_value = update_coordinate_function(coordinate, variable, *args)
            variable[coordinate] = new_coordinate_value
            if abs(new_coordinate_value - old_coordinate_value) < self.convergence_error:
                unchanged.add(coordinate)
            else:
                unchanged.clear()

        return variable

    def coordinate_descent(self,
        partial_derivative_function: Callable[[float, *tuple[Any, ...]], float],
        initialization: NDArray[np.float64],
        get_partial_derivative_args: Callable[[int, NDArray[np.float64], *tuple[Any, ...]], tuple[Any, ...]] | None = None,
        get_update_coordinate_function_args: Callable[[int, NDArray[np.float64]], tuple[Any, ...]] | None =None,
        updated_coordinates: list[int] | None =None,
    ) -> NDArray[np.float64]:
        """Minimize a loss function with coordinate descent,
        by leveraging the partial derivatives of the loss

        Parameters
        ----------
        partial_derivative: jitted callable
            (value: float, partial_derivative_args: Tuple) -> float
            Returns the partial derivative of the loss to optimize
        get_partial_derivative_args: callable(
                coordinate: int, 
                variable: NDArray,
                coordinate_update_args: Tuple
            ) -> (partial_derivative_args: Tuple)
            retrieves the arguments needed to optimize `variable` along `coordinate`
        get_update_coordinate_function_args: callable
            (coordinate: int, variable: NDArray) -> (coordinate_update_args: tuple)
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
        
        
        if get_partial_derivative_args is None:
            get_partial_derivative_args = empty_function
            
        if get_update_coordinate_function_args is None:
            get_update_coordinate_function_args = empty_function
            
        def update_coordinate_function(
            coordinate: int, 
            variable: NDArray[np.float64], 
            *coordinate_update_args: Any
        ) -> float:
            return njit_brentq(
                f=partial_derivative_function,
                args=get_partial_derivative_args(coordinate, variable, *coordinate_update_args),
                xtol=self.convergence_error,
                a=variable[coordinate] - 1.0,
                b=variable[coordinate] + 1.0
            )
            
        return self.updates(
            update_coordinate_function=update_coordinate_function,
            get_update_coordinate_function_args=get_update_coordinate_function_args,
            initialization=initialization,
            updated_coordinates=updated_coordinates,
        )

    def __call__(self, 
        init: NDArray[np.float64], 
        args: tuple[Any, ...] = (), 
        loss: Callable[[NDArray[np.float64], *tuple[Any, ...]], float] | None = None,
        gradient_function: Callable[[NDArray[np.float64], *tuple[Any, ...]], NDArray[np.float64]] | None = None,
        partial_derivative: Callable[[int, NDArray[np.float64], *tuple[Any, ...]], Callable[[float, *tuple[Any, ...]], float]] | None = None,
    ) -> NDArray[np.float64]:
        
        assert partial_derivative is not None

        def update_coordinate_function(coordinate: int, variable: NDArray[np.float64], *args: Any) -> float:
            return njit_brentq(
                f=partial_derivative(coordinate, variable, *args),
                xtol=self.convergence_error,
                a=variable[coordinate] - 1.0,
                b=variable[coordinate] + 1.0
            )
            
        return self.updates(update_coordinate_function, init)
    