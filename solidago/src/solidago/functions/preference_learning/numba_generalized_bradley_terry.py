from abc import abstractmethod
from functools import cached_property
from typing import Callable

import numpy as np
import numpy.typing as npt
from numba import njit

from solidago.poll import *
from solidago.primitives.optimize import coordinate_descent
from .generalized_bradley_terry import GeneralizedBradleyTerry, UniformGBT


class NumbaCoordinateDescentGBT(GeneralizedBradleyTerry):
    def __init__(self, 
        prior_std: float=7.0,
        uncertainty_nll_increase: float=1.0,
        max_uncertainty: float=1e3,
        convergence_error: float=1e-5,
        max_workers: int=1,
    ):
        """ Generalized Bradley Terry is a class of porbability models of comparisons,
        introduced in the paper "Generalized Bradley-Terry Models for Score Estimation 
        from Paired Comparisons" by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang
        and Oscar Villemaud, and published at AAAI'24.
        
        This implementation leverages coordinate descent, and makes heavy use of numba 
        to accelerate the computations.
        
        Parameters
        ----------
        prior_std: float=7.0
            Typical scale of values. 
            Technical, it should be the standard deviation of the gaussian prior.
        convergence_error: float=1e-5
            Admissible error in value computations (obtained through optimization).
        high_likelihood_range_threshold: float=1.0
            To determine the uncertainty, we compute left_unc (respectively, right_unc)
            such that value - left_unc (respectively, + right_unc) has a likelihood
            which is exp(high_likelihood_range_threshold) times lower than value.
        max_uncertainty: float=1e3
            Replaces infinite uncertainties with max_uncertainty
        """
        super().__init__(
            prior_std=prior_std,
            uncertainty_nll_increase=uncertainty_nll_increase,
            max_uncertainty=max_uncertainty,
            max_workers=max_workers,
        )
        self.convergence_error = convergence_error

    @property
    @abstractmethod
    def cumulant_generating_function_derivative(self) -> Callable[[npt.NDArray], npt.NDArray]:
        """ To use numba, instead of defining directly the cgf derivative,
        it is useful to instead define this method as a property,
        which outputs a jitted callable function.
        This callable function must have the following annocations.
        
        Parameters
        ----------
        value_diffs: npt.NDArray
            Score differences
            
        Returns
        -------
        cgf_derivative: npt.NDArray
            cgf_derivative[i] is the derivative of the cumulant-generating function 
            at value_diffs[i]
        """
        raise NotImplemented

    def compute_values(self,
        entities: Entities,
        comparisons: Comparisons, # keynames == ["entity_name", "other_name"]
        init : MultiScore, # keynames == "entity_name"
    ) -> npt.NDArray:
        """ Computes the values of the entities given comparisons """
        get_args = self.get_partial_derivative_args(entities, comparisons)
        return coordinate_descent(
            self.partial_derivative,
            self.init_values(entities, init),
            get_args,
            error=self.convergence_error,
        )
    
    def get_partial_derivative_args(self, 
        entities: Entities, 
        comparisons: Comparisons, # keynames == ["entity_name", "other_name"]
    ) -> Callable[[int, np.ndarray], tuple[np.ndarray, np.ndarray]]:
        
        indices = comparisons.compared_entity_indices(entities) # defaultdict[int, list]
        indices = [ indices[i] for i in range(len(entities)) ]
        normalized_comparisons = comparisons.entity_normalized_comparisons(entities) # defaultdict
        normalized_comparisons = [ np.array(normalized_comparisons[i]) for i in range(len(entities)) ]

        def f(entity_index: int, values: np.ndarray) -> tuple[np.array, np.array]:
            """ Returns compared_values and normalized_comparisons against compared entities """
            return values[indices[entity_index]], normalized_comparisons[entity_index]
            
        return f

    @cached_property
    def partial_derivative(self) -> Callable[[float, np.ndarray, np.ndarray], float]:
        """ Computes the partial derivative along a coordinate, 
        for a given value along the coordinate,
        when other coordinates' values are given by the solution.
        The computation evidently depends on the dataset,
        which is given by coordinate_comparisons.
        """
        prior_var = self.prior_std**2
        cgf_deriv = self.cumulant_generating_function_derivative

        @njit
        def njit_partial_derivative(
            entity_value: float,
            compared_values: npt.NDArray, 
            normalized_comparisons: npt.NDArray, 
        ) -> npt.NDArray:
            value_diffs = entity_value - compared_values
            nll_derivative = np.sum(cgf_deriv(value_diffs) + normalized_comparisons)
            prior_derivative = entity_value / prior_var
            return prior_derivative + nll_derivative
        
        return njit_partial_derivative

    def gradient(self, values: float, entities: Entities, comparisons: Comparisons) -> np.array:
        """ comparisons.keynames == ["entity_name", "other_name"] """
        get_args = self.get_partial_derivative_args(entities, comparisons)
        gradient = np.zeros(len(values))
        for entity_index in range(len(values)):
            args = get_args(entity_index, values)
            gradient[entity_index] = self.partial_derivative(values[entity_index], *args)
        return gradient
            

class NumbaUniformGBT(NumbaCoordinateDescentGBT, UniformGBT):
    def __init__(self,
        prior_std: float=7.0,
        uncertainty_nll_increase: float=1.0,
        max_uncertainty: float=1e3,
        convergence_error: float=1e-5,
        max_workers: int=1,
    ):
        """ Generalized Bradley Terry with a uniform root law is a straightforward
        instance of the models introduced in the paper "Generalized Bradley-Terry 
        Models for Score Estimation from Paired Comparisons" by Julien Fageot, 
        Sadegh Farhadkhani, Lê-Nguyên Hoang and Oscar Villemaud, and published at AAAI'24.
        
        This implementation leverages coordinate descent, and makes heavy use of numba 
        to accelerate the computations.
        
        Parameters
        ----------
        prior_std: float=7.0
            Typical scale of values. 
            Technical, it should be the standard deviation of the gaussian prior.
        convergence_error: float=1e-5
            Admissible error in value computations (obtained through optimization).
        high_likelihood_range_threshold: float=1.0
            To determine the uncertainty, we compute left_unc (respectively, right_unc)
            such that value - left_unc (respectively, + right_unc) has a likelihood
            which is exp(high_likelihood_range_threshold) times lower than value.
        max_uncertainty: float=1e3
            Replaces infinite uncertainties with max_uncertainty
        """
        super().__init__(
            prior_std=prior_std,
            uncertainty_nll_increase=uncertainty_nll_increase,
            max_uncertainty=max_uncertainty,
            convergence_error=convergence_error,
            max_workers=max_workers,
        )

    @cached_property
    def cumulant_generating_function_derivative(self) -> Callable[[npt.NDArray], npt.NDArray]:
        """ The cgf derivative of UniformGBT is simply 1 / tanh(value_diff) - 1 / value_diff.
        However, numerical accuracy requires care in the cases 
        where abs(value_diff) is small (because of division by zero).
        Moreover, as this method is widely used in Numba coordinate descent,
        and as it must be njit to be used by coordinate_descent,
        we write it as a cached property njit function.
        """
        @njit
        def njit_cumulant_generating_function_derivative(value_diffs: npt.NDArray):
            return np.where(
                np.abs(value_diffs) < 1e-2,
                value_diffs / 3,
                1 / np.tanh(value_diffs) - 1 / value_diffs,
            )

        return njit_cumulant_generating_function_derivative
