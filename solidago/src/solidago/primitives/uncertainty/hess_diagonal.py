from typing import Callable, Any
from numpy.typing import NDArray

from solidago.primitives.uncertainty.uncertainty_evaluator import UncertaintyEvaluator


class HessDiagonal(UncertaintyEvaluator):
    def __call__(self, 
        values: NDArray, 
        args: tuple,
        translated_loss: Callable[[int, NDArray, Any], Callable[[float], float]] | None = None,
        translated_prior: Callable[[int, NDArray, Any], Callable[[float], float]] | None = None,
        hess_diagonal: Callable[[NDArray, Any], NDArray] | None = None,
    ) -> tuple[NDArray, NDArray]:
        return hess_diagonal(values, *args)