from typing import Callable, Any
import numpy as np
from numpy.typing import NDArray

from solidago.primitives.uncertainty.uncertainty_evaluator import UncertaintyEvaluator, CwLossGetter


class HessDiagonal(UncertaintyEvaluator):
    def __call__(self, 
        values: NDArray[np.float64], 
        args: tuple[Any, ...],
        cw_prior_loss_getter: CwLossGetter | None = None,
        cw_nll_loss_getter: CwLossGetter | None = None,
        hess_diagonal: Callable[[NDArray[np.float64], *tuple[Any, ...]], NDArray[np.float64]] | None = None,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        assert hess_diagonal is not None
        uncertainties = hess_diagonal(values, *args)
        return uncertainties, uncertainties
    