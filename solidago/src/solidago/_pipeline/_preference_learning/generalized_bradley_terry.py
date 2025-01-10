from abc import abstractmethod
from functools import cached_property
from typing import Optional, Callable, Union, Mapping

import pandas as pd
import numpy as np
import numpy.typing as npt

import solidago.primitives.dichotomy as dichotomy

from solidago._state import *
from .base import PreferenceLearning


class GeneralizedBradleyTerry(PreferenceLearning):
    def __init__(self, 
        prior_std_dev: float=7.0,
        uncertainty_nll_increase: float=1.0,
        max_uncertainty: float=1e3,
        last_comparison_only: bool=True,
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
            Typical scale of scores. 
            Technical, it should be the standard deviation of the gaussian prior.
        uncertainty_nll_increase: float=1.0
            To determine the uncertainty, we compute left_unc (respectively, right_unc)
            such that score - left_unc (respectively, + right_unc) has a likelihood
            which is exp(uncertainty_nll_increase) times lower than score.
        max_uncertainty: float=1e3
            Replaces infinite uncertainties with max_uncertainty
        last_comparison_only: bool=True
            Ignores all comparisons between two entities prior to the last provided.
        """
        self.prior_std_dev = prior_std_dev
        self.uncertainty_nll_increase = uncertainty_nll_increase
        self.max_uncertainty = max_uncertainty
        self.last_comparison_only = last_comparison_only

    @abstractmethod
    def cumulant_generating_function_derivative(self, score_diffs: Mapping[int, float]) -> Mapping[int, float]:
        """ The beauty of the generalized Bradley-Terry model is that it suffices
        to specify its cumulant generating function derivative to fully define it,
        and to allow a fast computation of its corresponding maximum a posterior.
        This method performs the coordinate-wise computation of the cfg derivative
        at the score_diffs values. It is vectorized for improved performance,
        as it is expected to be repeatedly called.
        
        Note that entities are abstracted away from this method.
        
        Parameters
        ----------
        score_diffs: Mapping[int, float]
            Score differences
            
        Returns
        -------
        cgf_derivative: Mapping[int, float]
            cgf_derivative[i] is the derivative of the cumulant-generating function 
            at score_diffs[i]
        """

    @abstractmethod
    def cumulant_generating_function(self, score_diffs: Mapping[int, float]) -> float:
        """ The cumulant-generating function is useful to compute the uncertainty,
        especially if we use uncertainties by increase of the negative log-likelihood.
        It is also sufficient if the optimizer can compute the derivatives itself,
        e.g. when using pytorch.
        
        Parameters
        ----------
        score_diffs: Mapping[int, float]
            Score differences
            
        Returns
        -------
        cgf: Mapping[int, float]
            cgf[i] is the cumulant-generating function at score_diffs[i]
        """

    @abstractmethod
    def compute_scores(self, 
        entities: Entities,
        entity_name2index: dict[str, int],
        comparisons: Comparisons, # key_names == ["left_name, right_name"]
        init_multiscores : MultiScore, # key_names == "entity_name"
    ) -> npt.NDArray:
        """ Computes the scores given comparisons, typically by minimizing the
        user's negative log-posterior. This method is abstract, because 
        different optimizers may be used.
        
        Returns
        -------
        scores: npt.NDArray
        """
        raise NotImplementedError

    def user_learn(self, 
        user: User, # Not used (kept because other methods might leverage user metadata)
        entities: Entities,
        assessments: Assessments, # Not used
        comparisons: Comparisons, # key_names == ["criterion", "left_name", "right_name"]
        init_model: BaseModel,
    ) -> DirectScoring:
        """ Learns only based on comparisons """
        model = DirectScoring()
        compared_entity_names = comparisons.get_set("left_name") | comparisons.get_set("right_name")
        entities = entities.get(compared_entity_names) # Restrict to compared entities
        init = init_model(entities).reorder_keys(["criterion", "entity_name"])
        comparisons = comparisons.reorder_keys(["criterion", "left_name", "right_name"])
        criteria = comparisons.get_set("criterion") | init.get_set("criterion")
        for criterion in criteria:
            learned_scores = self.user_learn_criterion(entities, comparisons[criterion], init[criterion])
            for entity_name, score in learned_scores:
                if not score.isnan():
                    model[entity_name, criterion] = score
        return model

    def init_scores(self, 
        entity_name2index: dict[str, int],
        init_multiscores: MultiScore, # key_names == "entity_name"
    ) -> npt.NDArray:
        scores = np.zeros(len(entity_name2index), dtype=np.float64)
        for entity, init_score in init_multiscores:
            if not init_score.isnan():
                scores[entity_name2index[str(entity)]] = init_score.value
        return scores
    
    def user_learn_criterion(self, 
        entities: Entities,
        comparisons: Comparisons, # key_names == ["left_name, right_name"]
        init_multiscores: MultiScore, # key_names == ["entity_name"]
    ) -> MultiScore: # key_names == ["entity_name"]
        """
        Returns
        -------
        out: dict
            out[entity_name] must be of type Score (i.e. with a value and left/right uncertainties
        """
        entity_name2index = { str(entity): index for index, entity in enumerate(entities) }
        scores = self.compute_scores(entities, entity_name2index, comparisons, init_multiscores)
        lefts, rights = self.compute_uncertainties(entities, entity_name2index, comparisons, scores)
        return MultiScore({
            entities.iloc[i].name: (scores[i], lefts[i], rights[i])
            for i in range(len(scores))
        }, key_names=["entity_name"])
    
    def compute_uncertainties(self,
        entities: Entities,
        entity_name2index: dict[str, int],
        comparisons: Comparisons, # key_names == ["left_name, right_name"]
        scores: npt.NDArray,
    ) -> tuple[npt.NDArray, npt.NDArray]:
        """ Given learned maximum-a-posteriori scores, this method determines uncertainties
        by evaluating the necessary deviations to decrease the log likelihood
        by the amount `self.uncertainty_nll_increase`.
        
        Returns
        -------
        lefts: npt.NDArray
            lefts[i] is the left uncertainty on scores[i]
        rights: npt.NDArray
            rights[i] is the right uncertainty on scores[i]
        """
        indices = comparisons.compared_entity_indices(entity_name2index, self.last_comparison_only)
        indices = { loc: np.array(indices[loc]) for loc in ("left", "right") }
        score_diffs = scores[indices["left"]] - scores[indices["right"]]
        normalized_comparisons = comparisons.normalized_comparisons(self.last_comparison_only)
        score_negative_log_likelihood = self.negative_log_likelihood(score_diffs, normalized_comparisons)
        
        kwargs = dict(
            f=self.translated_negative_log_likelihood,
            value=score_negative_log_likelihood + self.uncertainty_nll_increase,
            error=1e-1,
        )

        lefts = np.empty_like(scores)
        rights = np.empty_like(scores)
        for i in range(len(scores)):
            indicators = 1 *(indices["left"] == i) - 1 *(indices["right"] == i)
            kwargs["args"] = (score_diffs, normalized_comparisons, indicators)
            try:
                lefts[i] = - dichotomy.solve(xmin=-self.max_uncertainty, xmax=0.0, **kwargs)
            except ValueError:
                lefts[i] = self.max_uncertainty

            try:
                rights[i] = dichotomy.solve(xmin=0.0, xmax=self.max_uncertainty, **kwargs)
            except ValueError:
                rights[i] = self.max_uncertainty
                
        return lefts, rights

    def negative_log_likelihood(self, 
        score_diffs: Mapping[int, float], 
        normalized_comparisons: Mapping[int, float]
    ) -> float:
        """ Computes the negative log-likelihood of the observed 
        comparisons (`normalized_comparisons`) given the score differences
        between the entities that are compared.
        Necessary only for the uncertainty estimators (the cumulant-generating
        function derivative is sufficient to compute the maximum a posteriori).
        
        Note that entities are abstracted away from this method,
        and the prior is not added.
        
        Parameters
        ----------
        score_diffs: npt.NDArray
            Score differences
        normalized_comparisons: npt.NDArray
            Normalized comparison values
        
        Returns
        -------
        log_likelihood: float
            Logarithm of the likelihood of the comparisons given the score differences
        """
        cgfs = self.cumulant_generating_function(score_diffs)
        return (score_diffs * normalized_comparisons + cgfs).sum()
        
    def translated_negative_log_likelihood(self,
        delta: float,
        score_diffs: Mapping[int, float],
        normalized_comparisons: Mapping[int, float],
        indicators: npt.NDArray,
    ) -> float:
        """This function is a convex negative log likelihood, translated such
        that its minimum has a constant negative value at `delta=0`. The
        roots of this function are used to compute the uncertainties
        intervals. If it has only a single root, then uncertainty on the
        other side is considered infinite.
        
        Note that the negative log-likelihood function is actually translated
        in both the input space (as deviations from score_diffs for one entity
        score deviation) and the output space (by subtracting the negative
        log-likelihood at score_diffs, and self.high_likelihood_range_threshold
        to mean that the roots have a likelihood that is
        exp(self.high_likelihood_range_threshold) times smaller
        than that of score_diffs.
        
        Note that entities are abstracted away, though indicators should
        be carefully computed as a function of the entity whose score uncertainity
        is being estimated.
        """
        deviated_score_diffs = indicators * delta + score_diffs
        return self.negative_log_likelihood(deviated_score_diffs, normalized_comparisons)


class UniformGBT(GeneralizedBradleyTerry):
    def __init__(self,
        prior_std_dev: float = 7.0,
        uncertainty_nll_increase: float = 1.0,
        max_uncertainty: float=1e3,
        last_comparison_only: bool=True,
    ):
        """ UniformGBT is the specific instance of the generalized Bradley-Terry models
        with a uniform distribution over [-1, 1] as a root law. Find out more 
        in the paper "Generalized Bradley-Terry Models for Score Estimation 
        from Paired Comparisons" by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang
        and Oscar Villemaud, and published at AAAI'24.
        
        
        Parameters
        ----------
        prior_std_dev: float=7.0
            Typical scale of scores. 
            Technical, it should be the standard deviation of the gaussian prior.
        uncertainty_nll_increase: float=1.0
            To determine the uncertainty, we compute left_unc (respectively, right_unc)
            such that score - left_unc (respectively, + right_unc) has a likelihood
            which is exp(uncertainty_nll_increase) times lower than score.
        max_uncertainty: float=1e3
            Replaces infinite uncertainties with max_uncertainty
        last_comparison_only: bool=True
            Ignores all comparisons between two entities prior to the last provided.
        """
        super().__init__(
            prior_std_dev=prior_std_dev,
            uncertainty_nll_increase=uncertainty_nll_increase,
            max_uncertainty=max_uncertainty,
            last_comparison_only=last_comparison_only,
        )
    
    def cumulant_generating_function(self, score_diffs: npt.NDArray) -> npt.NDArray:
        """ The cgf of UniformGBT is simply log( sinh(score_diff) / score_diff ).
        However, numerical accuracy requires care in the cases 
        where abs(score_diff) is small (because of division by zero)
        or where it is large (because sinh explodes).
        """
        score_diffs_abs = np.abs(score_diffs)
        return np.where(
            score_diffs_abs > 1e-1,
            np.where(
                score_diffs_abs < 20.0,
                np.log(np.sinh(score_diffs) / score_diffs),
                score_diffs_abs - np.log(2) - np.log(score_diffs_abs),
            ),
            score_diffs_abs ** 2 / 6 - score_diffs_abs ** 4 / 180,
        )

    def cumulant_generating_function_derivative(self, score_diffs: npt.NDArray) -> npt.NDArray:
        """ The cgf derivative of UniformGBT is simply 
        1 / tanh(score_diff) - 1 / score_diff.
        However, numerical accuracy requires care in the cases 
        where abs(score_diff) is small (because of division by zero).
        """
        return np.where(
            np.abs(score_diffs) < 1e-2,
            score_diffs / 3,
            1 / np.tanh(score_diffs) - 1 / score_diffs,
        )
