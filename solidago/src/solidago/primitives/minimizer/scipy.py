from typing import Any, Callable
from numpy.typing import NDArray
from scipy.optimize import minimize

import numpy as np

from solidago.primitives.minimizer.minimizer import Minimizer


class SciPyMinimizer(Minimizer):
    def __init__(self, method: str="L-BFGS-B", convergence_error: float=1e-5):
        assert isinstance(method, str), method
        assert isinstance(convergence_error, float), convergence_error
        self.method = method
        self.convergence_error = convergence_error

    def __call__(self, 
        init: NDArray[np.float64], 
        args: tuple[Any, ...] = (), 
        loss: Callable[[NDArray[np.float64], *tuple[Any, ...]], float] | None = None,
        gradient_function: Callable[[NDArray[np.float64], *tuple[Any, ...]], NDArray[np.float64]] | None = None,
        partial_derivative: Callable[[int, NDArray[np.float64], *tuple[Any, ...]], Callable[[float, *tuple[Any, ...]], float]] | None = None, # not used
    ) -> NDArray[np.float64]:
        assert loss is not None and gradient_function is not None
        result = minimize(loss, init, args, self.method, gradient_function)
        return result.x
    