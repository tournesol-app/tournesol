import numpy as np
from numpy.typing import NDArray
from typing import Any, Callable

from solidago.primitives import dichotomy
from solidago.primitives.uncertainty.uncertainty_evaluator import UncertaintyEvaluator


class UncertaintyByLossIncrease(UncertaintyEvaluator):
    def __init__(self, nll_increase: float=1.0, error: float=1e-1, max: float=1e3):
        self.nll_increase = float(nll_increase)
        self.error = float(error)
        self.max = float(max)

    def __call__(self, 
        values: NDArray, 
        args: tuple,
        translated_loss: Callable[[int, NDArray, Any], Callable[[float], float]] | None = None,
        translated_prior: Callable[[int, NDArray, Any], Callable[[float], float]] | None = None, # not used
        hess_diagonal: Callable[[NDArray, Any], NDArray] | None = None, # not used
    ) -> tuple[NDArray, NDArray]:
        return self.compute_uncertainties(values, args, self.loss(translated_loss, translated_prior))

    def loss(self,
        translated_loss: Callable[[int, NDArray, Any], Callable[[float], float]] | None = None,
        translated_prior: Callable[[int, NDArray, Any], Callable[[float], float]] | None = None,
    ) -> Callable[[int, NDArray, Any], Callable[[float], float]]:
        def f(value_index: int, values: NDArray, *args) -> float:
            def g(delta: float) -> float:
                loss = translated_loss(value_index, values, *args)(delta)
                prior = translated_prior(value_index, values, *args)(delta)
                return loss + prior
            return g
        return f

    def compute_uncertainties(self,
        values: NDArray, 
        args: tuple,
        loss: Callable[[int, NDArray, Any], Callable[[float], float]] | None = None,        
    ) -> tuple[NDArray, NDArray]:
        lefts, rights = np.empty_like(values), np.empty_like(values)
        for i in range(len(values)):
            f = loss(i, values, *args)
            target_value = f(0.0) + self.nll_increase
            lefts[i] = self.solve(f, target_value, -self.max, 0.0)
            rights[i] = self.solve(f, target_value, 0.0, self.max)
        return lefts, rights
    
    def solve(self, 
        f: Callable[[float], float], 
        target_value: float, 
        xmin: float, 
        xmax: float,
    ) -> float:
        try:
            return np.abs(dichotomy.solve(f, target_value, xmin, xmax, self.error))
        except ValueError:
            return self.max


class NLLIncrease(UncertaintyByLossIncrease):
    def __init__(self, nll_increase: float=1.0, error: float=1e-1, max: float=1e3):
        self.nll_increase = float(nll_increase)
        self.error = float(error)
        self.max = float(max)

    def loss(self,
        translated_loss: Callable[[int, NDArray, Any], Callable[[float], float]] | None = None,
        translated_prior: Callable[[int, NDArray, Any], Callable[[float], float]] | None = None, # Not used
    ) -> Callable[[int, NDArray, Any], Callable[[float], float]]:
        return translated_loss