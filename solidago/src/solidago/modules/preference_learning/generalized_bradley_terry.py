from abc import abstractmethod
from functools import cached_property
from typing import Optional, Callable, Union, Mapping

import pandas as pd
import numpy as np
import numpy.typing as npt

import solidago.primitives.dichotomy as dichotomy

from solidago.state import *
from .base import PreferenceLearning


class GeneralizedBradleyTerry(PreferenceLearning):
    def __init__(self, 
        prior_std_dev: float=7.0,
        uncertainty_nll_increase: float=1.0,
        max_uncertainty: float=1e3,
    ):
        """ Generalized Bradley Terry is a class of porbability models of comparisons,
        introduced in the paper "Generalized Bradley-Terry Models for Score Estimation 
        from Paired Comparisons" by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang
        and Oscar Villemaud, and published at AAAI'24.
        
        Note that this class only defines the key objects of Generalized Bradley Terry,
        without specification of (1) the root law and (2) the optimization method to
        compute the maximum a posteriori. Nevertheless, it does implement uncertainty
        estimation given the maximum a posteriori, using dichotomic search.
        
        Parameters
        ----------
        prior_std_dev: float=7.0
            Typical scale of score values. 
            Technical, it should be the standard deviation of the gaussian prior.
        uncertainty_nll_increase: float=1.0
            To determine the uncertainty, we compute left_unc (respectively, right_unc)
            such that value - left_unc (respectively, + right_unc) has a likelihood
            which is exp(uncertainty_nll_increase) times lower than value.
        max_uncertainty: float=1e3
            Replaces infinite uncertainties with max_uncertainty
        """
        self.prior_std_dev = prior_std_dev
        self.uncertainty_nll_increase = uncertainty_nll_increase
        self.max_uncertainty = max_uncertainty

    @abstractmethod
    def cumulant_generating_function_derivative(self, value_diffs: npt.NDArray) -> npt.NDArray:
        """ The beauty of the generalized Bradley-Terry model is that it suffices
        to specify its cumulant generating function derivative to fully define it,
        and to allow a fast computation of its corresponding maximum a posterior.
        This method performs the coordinate-wise computation of the cfg derivative
        at the value_diffs values. It is vectorized for improved performance,
        as it is expected to be repeatedly called.
        
        Note that entities are abstracted away from this method.
        
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

    @abstractmethod
    def cumulant_generating_function(self, value_diffs: npt.NDArray) -> float:
        """ The cumulant-generating function is useful to compute the uncertainty,
        especially if we use uncertainties by increase of the negative log-likelihood.
        It is also sufficient if the optimizer can compute the derivatives itself,
        e.g. when using pytorch.
        
        Parameters
        ----------
        value_diffs: Mapping[int, float]
            Score differences
            
        Returns
        -------
        cgf: Mapping[int, float]
            cgf[i] is the cumulant-generating function at value_diffs[i]
        """

    @abstractmethod
    def compute_values(self,
        entities: Entities,
        comparisons: Comparisons, # keynames == ["entity_name", "other_name"]
        init : MultiScore, # keynames == "entity_name"
    ) -> npt.NDArray:
        """ Computes the values given comparisons, typically by minimizing the
        user's negative log-posterior. This method is abstract, because 
        different optimizers may be used.
        
        Returns
        -------
        values: npt.NDArray
        """
        raise NotImplementedError

    def user_learn(self, 
        user: User, # Not used (kept because other methods might leverage user metadata)
        entities: Entities,
        assessments: Assessments, # Not used
        comparisons: Comparisons, # keynames == ["criterion", "entity_name", "other_name"]
        init_model: Optional[ScoringModel]=None,
    ) -> DirectScoring:
        """ Learns only based on comparisons """
        init_model = DirectScoring() if init_model is None else init_model
        model = DirectScoring()
        comparisons.cache("criterion", "entity_name", "other_name")
        for (criterion,), criterion_comparisons in comparisons.iter("criterion"):
            criterion_entity_names = criterion_comparisons.keys("entity_name")
            if len(criterion_entity_names) <= 1:
                continue
            criterion_entities = entities.get(criterion_entity_names) # Restrict to compared entities
            init = init_model(criterion_entities, criterion)
            scores = self.user_learn_criterion(criterion_entities, criterion_comparisons, init)
            for (entity_name,), score in scores:
                if not score.isnan():
                    model[entity_name, criterion] = score
        return model
    
    def user_learn_criterion(self, 
        entities: Entities,
        comparisons: Comparisons, # keynames == ["left_name, right_name"]
        init: Optional[MultiScore]=None, # keynames == ["entity_name"]
    ) -> MultiScore: # keynames == ["entity_name"]
        """
        Returns
        -------
        out: dict
            out[entity_name] must be of type Score (i.e. with a value and left/right uncertainties
        """
        init = MultiScore("entity_name") if init is None else init
        values = self.compute_values(entities, comparisons, init)
        lefts, rights = self.compute_uncertainties(entities, comparisons, values)
        return MultiScore("entity_name", {
            entities.iloc[i].name: Score(values[i], lefts[i], rights[i])
            for i in range(len(values)) 
            if not (lefts[i] == self.max_uncertainty and lefts[i] == self.max_uncertainty)
        })

    def init_values(self, entities: Entities, init: MultiScore) -> npt.NDArray:
        values = np.zeros(len(entities), dtype=np.float64)
        for entity, index in entities.name2index.items():
            if not np.isnan(init[entity].value):
                values[index] = init[entity].value
        return values
    
    def compute_uncertainties(self,
        entities: Entities,
        comparisons: Comparisons, # keynames == ["left_name, right_name"]
        values: npt.NDArray,
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """ Given learned maximum-a-posteriori values, this method determines uncertainties
        by evaluating the necessary deviations to decrease the log likelihood
        by the amount `self.uncertainty_nll_increase`.
        
        Returns
        -------
        lefts: npt.NDArray
            lefts[i] is the left uncertainty on values[i]
        rights: npt.NDArray
            rights[i] is the right uncertainty on values[i]
        """
        if not comparisons:
            inf_array = np.array([ float("inf") for _ in entities ])
            return inf_array, inf_array

        compared_entity_indices = comparisons.compared_entity_indices(entities)
        entity_normalized_comparisons = comparisons.entity_normalized_comparisons(entities)
                
        lefts, rights = np.empty_like(values), np.empty_like(values)
        kwargs = dict(f=self.translated_negative_log_likelihood, error=1e-1)
        def solve(**kwargs): 
            try: return np.abs(dichotomy.solve(**kwargs))
            except ValueError: return self.max_uncertainty
            
        for entity_index in range(len(values)):
            value_diffs = values[entity_index] - values[compared_entity_indices[entity_index]]
            normalized_comparisons = np.array(entity_normalized_comparisons[entity_index])
            nll = self.translated_negative_log_likelihood(0., value_diffs, normalized_comparisons) 
            kwargs["args"] = (value_diffs, normalized_comparisons)
            kwargs["value"] = nll + self.uncertainty_nll_increase
            lefts[entity_index] = solve(xmin=-self.max_uncertainty, xmax=0.0, **kwargs)
            rights[entity_index] = solve(xmin=0.0, xmax=self.max_uncertainty, **kwargs)
                
        return lefts, rights

    def negative_log_likelihood(self, value_diffs: npt.NDArray, normalized_comparisons: npt.NDArray) -> float:
        """ Computes the negative log-likelihood of the observed 
        comparisons (`normalized_comparisons`) given the value differences
        between the entities that are compared.
        Necessary only for the uncertainty estimators (the cumulant-generating
        function derivative is sufficient to compute the maximum a posteriori).
        
        Note that entities are abstracted away from this method,
        and the prior is not added.
        
        Parameters
        ----------
        value_diffs: npt.NDArray
            Score differences
        normalized_comparisons: npt.NDArray
            Normalized comparison values
        
        Returns
        -------
        log_likelihood: float
            Logarithm of the likelihood of the comparisons given the value differences
        """
        cgfs = self.cumulant_generating_function(value_diffs)
        return (value_diffs * normalized_comparisons + cgfs).sum()
        
    def translated_negative_log_likelihood(self,
        delta: float,
        value_diffs: npt.NDArray,
        normalized_comparisons: npt.NDArray,
    ) -> float:
        """This function is a convex negative log likelihood, translated such
        that its minimum has a constant negative value at `delta=0`. The
        roots of this function are used to compute the uncertainties
        intervals. If it has only a single root, then uncertainty on the
        other side is considered infinite.
        
        Note that the negative log-likelihood function is actually translated
        in both the input space (as deviations from value_diffs for one entity
        value deviation) and the output space (by subtracting the negative
        log-likelihood at value_diffs, and self.high_likelihood_range_threshold
        to mean that the roots have a likelihood that is
        exp(self.high_likelihood_range_threshold) times smaller
        than that of value_diffs.
        
        Note that entities are abstracted away, though indicators should
        be carefully computed as a function of the entity whose value uncertainity
        is being estimated.
        """
        deviated_value_diffs = delta + value_diffs
        return self.negative_log_likelihood(deviated_value_diffs, normalized_comparisons)


class UniformGBT(GeneralizedBradleyTerry):
    def __init__(self,
        prior_std_dev: float = 7.0,
        uncertainty_nll_increase: float = 1.0,
        max_uncertainty: float=1e3,
    ):
        """ UniformGBT is the specific instance of the generalized Bradley-Terry models
        with a uniform distribution over [-1, 1] as a root law. Find out more 
        in the paper "Generalized Bradley-Terry Models for Score Estimation 
        from Paired Comparisons" by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang
        and Oscar Villemaud, and published at AAAI'24.
        
        
        Parameters
        ----------
        prior_std_dev: float=7.0
            Typical scale of values. 
            Technical, it should be the standard deviation of the gaussian prior.
        uncertainty_nll_increase: float=1.0
            To determine the uncertainty, we compute left_unc (respectively, right_unc)
            such that value - left_unc (respectively, + right_unc) has a likelihood
            which is exp(uncertainty_nll_increase) times lower than value.
        max_uncertainty: float=1e3
            Replaces infinite uncertainties with max_uncertainty
        """
        super().__init__(
            prior_std_dev=prior_std_dev,
            uncertainty_nll_increase=uncertainty_nll_increase,
            max_uncertainty=max_uncertainty,
        )
    
    def cumulant_generating_function(self, value_diffs: npt.NDArray) -> npt.NDArray:
        """ The cgf of UniformGBT is simply log( sinh(value_diff) / value_diff ).
        However, numerical accuracy requires care in the cases 
        where abs(value_diff) is small (because of division by zero)
        or where it is large (because sinh explodes).
        """
        value_diffs_abs = np.abs(value_diffs)
        with np.errstate(all='ignore'):
            return np.where(
                value_diffs_abs > 1e-1,
                np.where(
                    value_diffs_abs < 20.0,
                    np.log(np.sinh(value_diffs) / value_diffs),
                    value_diffs_abs - np.log(2) - np.log(value_diffs_abs),
                ),
                value_diffs_abs ** 2 / 6 - value_diffs_abs ** 4 / 180,
            )

    def cumulant_generating_function_derivative(self, value_diffs: npt.NDArray) -> npt.NDArray:
        """ The cgf derivative of UniformGBT is simply 
        1 / tanh(value_diff) - 1 / value_diff.
        However, numerical accuracy requires care in the cases 
        where abs(value_diff) is small (because of division by zero).
        """
        return np.where(
            np.abs(value_diffs) < 1e-2,
            value_diffs / 3,
            1 / np.tanh(value_diffs) - 1 / value_diffs,
        )
