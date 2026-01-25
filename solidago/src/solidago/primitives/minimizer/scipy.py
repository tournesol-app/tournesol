from typing import Any, Callable
from numpy.typing import NDArray
from scipy.optimize import minimize

from solidago.primitives.minimizer.minimizer import Minimizer


class SciPyMinimizer(Minimizer):
    def __init__(self, method: str="L-BFGS-B", convergence_error: float=1e-5):
        assert isinstance(method, str), method
        assert isinstance(convergence_error, float), convergence_error
        self.method = method
        self.convergence_error = convergence_error

    def __call__(self, 
        init: NDArray, 
        args: tuple, 
        loss: Callable[[NDArray, Any], float],
        gradient_function: Callable[[NDArray, Any], NDArray],
        partial_derivative: Callable[[int, NDArray, Any], Callable[[float], float]], # not used
    ) -> NDArray:
        result = minimize(loss, init, args, self.method, gradient_function)
        return result.x