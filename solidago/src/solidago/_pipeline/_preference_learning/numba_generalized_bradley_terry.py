from abc import abstractmethod
from functools import cached_property
from typing import Optional, Callable, Union

import pandas as pd
import numpy as np
import numpy.typing as npt
from numba import njit

from solidago._state import *
from solidago.primitives.optimize import coordinate_descent, njit_brentq
from .generalized_bradley_terry import GeneralizedBradleyTerry, UniformGBT


class NumbaCoordinateDescentGBT(GeneralizedBradleyTerry):
    def __init__(self, 
        prior_std_dev: float=7.0,
        uncertainty_nll_increase: float=1.0,
        max_uncertainty: float=1e3,
        convergence_error: float=1e-5,
        last_comparison_only: bool=True,
    ):
        """ Generalized Bradley Terry is a class of porbability models of comparisons,
        introduced in the paper "Generalized Bradley-Terry Models for Score Estimation 
        from Paired Comparisons" by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang
        and Oscar Villemaud, and published at AAAI'24.
        
        This implementation leverages coordinate descent, and makes heavy use of numba 
        to accelerate the computations.
        
        Parameters
        ----------
        prior_std_dev: float=7.0
            Typical scale of scores. 
            Technical, it should be the standard deviation of the gaussian prior.
        convergence_error: float=1e-5
            Admissible error in score computations (obtained through optimization).
        high_likelihood_range_threshold: float=1.0
            To determine the uncertainty, we compute left_unc (respectively, right_unc)
            such that score - left_unc (respectively, + right_unc) has a likelihood
            which is exp(high_likelihood_range_threshold) times lower than score.
        max_uncertainty: float=1e3
            Replaces infinite uncertainties with max_uncertainty
        """
        super().__init__(
            prior_std_dev=prior_std_dev,
            uncertainty_nll_increase=uncertainty_nll_increase,
            max_uncertainty=max_uncertainty,
            last_comparison_only=last_comparison_only,
        )
        self.convergence_error = convergence_error

    @property
    @abstractmethod
    def cumulant_generating_function_derivative(self) -> Callable[[npt.NDArray], npt.NDArray]:
        """ To use numba, instead of defining directly the cgf derivative,
        it is useful to instead define this method as a property,
        which outputs a callable function decorated with @njit.
        This callable function must have the following annocations.
        
        Parameters
        ----------
        score_diffs: npt.NDArray
            Score differences
            
        Returns
        -------
        cgf_derivative: npt.NDArray
            cgf_derivative[i] is the derivative of the cumulant-generating function 
            at score_diffs[i]
        """
        raise NotImplemented

    def compute_scores(self, 
        entities: Entities,
        entity_name2index: dict[str, int],
        comparisons: Comparisons, # key_names == ["left_name, right_name"]
        init_multiscores : MultiScore, # key_names == "entity_name"
    ) -> npt.NDArray:
        """ Computes the scores given comparisons """
        comparisons = comparisons.order_by_entities()
        def get_partial_derivative_args(entity_index: int, scores: np.ndarray) -> tuple:
            entity_name = entities.iloc[entity_index].name
            normalized_comparisons = comparisons[entity_name].normalized_comparisons(self.last_comparison_only)
            df = comparisons[entity_name].to_df(last_row_only=self.last_comparison_only)
            indices = df["other_name"].map(entity_name2index)
            return scores[indices], np.array(normalized_comparisons)

        return coordinate_descent(
            self.partial_derivative,
            get_partial_derivative_args=get_partial_derivative_args,
            initialization=self.init_scores(entity_name2index, init_multiscores),
            error=self.convergence_error,
        )

    @cached_property
    def partial_derivative(self) -> Callable[[int, np.ndarray[np.float64], dict, dict], float]:
        """ Computes the partial derivative along a coordinate, 
        for a given value along the coordinate,
        when other coordinates' values are given by the solution.
        The computation evidently depends on the dataset,
        which is given by coordinate_comparisons.
        """
        prior_var = self.prior_std_dev**2
        cfg_deriv = self.cumulant_generating_function_derivative

        @njit
        def njit_partial_derivative(
            entity_index: int,
            scores: float,
            compared_scores: npt.NDArray, 
            normalized_comparisons: npt.NDArray, 
        ) -> npt.NDArray:
            score_diffs = scores[entity_index] - compared_scores
            nll_derivative = np.sum(cfg_deriv(score_diffs) - normalized_comparisons)
            prior_derivative = scores[entity_index] / prior_var
            return prior_derivative + nll_derivative
        
        return njit_partial_derivative


class NumbaUniformGBT(NumbaCoordinateDescentGBT, UniformGBT):
    def __init__(self,
        prior_std_dev: float=7.0,
        uncertainty_nll_increase: float=1.0,
        max_uncertainty: float=1e3,
        convergence_error: float=1e-5,
        last_comparison_only: bool=True,
    ):
        """

        Parameters (TODO)
        ----------
        """
        super().__init__(
            prior_std_dev=prior_std_dev,
            uncertainty_nll_increase=uncertainty_nll_increase,
            max_uncertainty=max_uncertainty,
            convergence_error=convergence_error,
            last_comparison_only=last_comparison_only,
        )

    @cached_property
    def cumulant_generating_function_derivative(self) -> Callable[[npt.NDArray], npt.NDArray]:
        """ The cgf derivative of UniformGBT is simply 1 / tanh(score_diff) - 1 / score_diff.
        However, numerical accuracy requires care in the cases 
        where abs(score_diff) is small (because of division by zero).
        Moreover, as this method is widely used in Numba coordinate descent,
        and as it must be njit to be used by coordinate_descent,
        we write it as a cached property njit function.
        """
        @njit
        def njit_cumulant_generating_function_derivative(score_diffs: npt.NDArray):
            return np.where(
                np.abs(score_diffs) < 1e-2,
                score_diffs / 3,
                1 / np.tanh(score_diffs) - 1 / score_diffs,
            )

        return njit_cumulant_generating_function_derivative
