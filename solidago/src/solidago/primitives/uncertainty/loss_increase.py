import numpy as np
import logging

logger = logging.getLogger(__name__)

from numpy.typing import NDArray
from typing import Any, Callable
from numba import njit

from solidago.primitives import dichotomy
from solidago.primitives.uncertainty.uncertainty_evaluator import UncertaintyEvaluator, CwLossGetter


class UncertaintyByLossIncrease(UncertaintyEvaluator):
    def __init__(self, loss_increase: float=1.0, error: float=1e-1, max: float=1e3):
        self.loss_increase = float(loss_increase)
        self.error = float(error)
        self.max = float(max)

    def __call__(self, 
        values: NDArray[np.float64], 
        args: tuple[Any, ...],
        cw_prior_loss_getter: CwLossGetter | None = None,
        cw_nll_loss_getter: CwLossGetter | None = None,
        hess_diagonal: Callable[[NDArray[np.float64], *tuple[Any, ...]], NDArray[np.float64]] | None = None, # not used
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        cw_loss, cw_loss_args = self.get_cw_loss_and_args(cw_prior_loss_getter, cw_nll_loss_getter, values, args)
        n_coordinates = len(values)
        self_args = n_coordinates, self.loss_increase, self.error, self.max
        compute_uncertainties = type(self).compute_uncertainties
        try:
            njit_compute = njit(compute_uncertainties)
            njit_dichotomy = njit(dichotomy.solve)
            njit_cw_loss = njit(cw_loss)
            return njit_compute(njit_dichotomy, njit_cw_loss, *self_args, *cw_loss_args) # type: ignore
        except:
            logger.info("Failed to jit uncertainty computation.")
            return compute_uncertainties(dichotomy.solve, cw_loss, *self_args, *cw_loss_args)

    def get_cw_loss_and_args(self,
        cw_prior_loss_getter: CwLossGetter | None,
        cw_nll_loss_getter: CwLossGetter | None,
        values: NDArray[np.float64],
        args: tuple[Any, ...],
    ) -> tuple[Callable[[float, np.int64, *tuple[Any, ...]], float], tuple[Any, ...]]:
        assert cw_prior_loss_getter is not None
        assert cw_nll_loss_getter is not None
        cw_prior_loss, cw_prior_loss_args = cw_prior_loss_getter(values, *args)
        cw_nll_loss, cw_nll_loss_args = cw_nll_loss_getter(values, *args)
        def cw_loss(delta: float, value_index: np.int64, *cw_loss_args: tuple[Any, ...]) -> float:
            return cw_prior_loss(delta, value_index, *cw_loss_args[0]) + cw_nll_loss(delta, value_index, *cw_loss_args[1])
        return cw_loss, (cw_prior_loss_args, cw_nll_loss_args)

    @staticmethod
    def compute_uncertainties(
        solve: Callable[[
            Callable[[float, *tuple[Any, ...]], float], 
            float, float, float, float, float | None, tuple[Any, ...]
        ], float],
        losses: Callable[[float, np.int64, *tuple[Any, ...]], float],
        n_coordinates: int, 
        nll_increase: float,
        error: float,
        max_uncertainty: float,
        *args: Any,
    ) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
        if n_coordinates == 0:
            return np.zeros(n_coordinates), np.zeros(n_coordinates)
        lefts, rights = np.empty(n_coordinates), np.empty(n_coordinates)
        target = losses(0., np.int64(0), *args) + nll_increase
        for i in range(n_coordinates):
            lefts[i] = np.abs(solve(losses, target, -max_uncertainty, 0., error, max_uncertainty, (i, *args))) # type: ignore
            rights[i] = np.abs(solve(losses, target, 0., max_uncertainty, error, max_uncertainty, (i, *args))) # type: ignore
        return lefts, rights


class NLLIncrease(UncertaintyByLossIncrease):
    def __init__(self, nll_increase: float=1.0, error: float=1e-1, max: float=1e3):
        super().__init__(nll_increase, error, max)

    def get_cw_loss_and_args(self,
        cw_prior_loss_getter: CwLossGetter | None, # not used
        cw_nll_loss_getter: CwLossGetter | None,
        values: NDArray[np.float64],
        args: tuple[Any, ...],
    ) -> tuple[Callable[[float, np.int64, *tuple[Any, ...]], float], tuple[Any, ...]]:
        assert cw_nll_loss_getter is not None
        return cw_nll_loss_getter(values, *args)
    