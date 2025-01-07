from abc import abstractmethod
from functools import cached_property
from typing import Optional, Callable, Union

import pandas as pd
import numpy as np
import numpy.typing as npt
from numba import njit

from solidago.state import *
from solidago.primitives.optimize import coordinate_descent, njit_brentq
from .base import PreferenceLearning


class GeneralizedBradleyTerry(PreferenceLearning):
    def __init__(self, 
        prior_std_dev: float=7.0,
        convergence_error: float=1e-5,
        high_likelihood_range_threshold: float=1.0,
        max_uncertainty: float=1e3
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
        self.prior_std_dev = prior_std_dev
        self.convergence_error = convergence_error
        self.high_likelihood_range_threshold = high_likelihood_range_threshold
        self.max_uncertainty = max_uncertainty

    @property
    @abstractmethod
    def cumulant_generating_function_derivative(self) -> Callable[[npt.NDArray], npt.NDArray]:
        """ The beauty of the generalized Bradley-Terry model is that it suffices
        to specify its cumulant generating function derivative to fully define it,
        and to allow a fast computation of its corresponding maximum a posterior.
        
        Parameters
        ----------
        score_diff: float
            Score difference
            
        Returns
        -------
        out: float
        """

    @property
    @abstractmethod
    def log_likelihood_function(self) -> Callable[[npt.NDArray, npt.NDArray], float]:
        """The loss function definition is used only to compute uncertainties.
        """

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
    ) -> np.ndarray:
        scores = np.zeros(len(entity_name2index))
        for entity, init_score in init_multiscores:
            if not init_score.isnan():
                scores[entity_name2index[str(entity)]] = init_score.value
        return scores
    
    def compute_scores(self, 
        entities: Entities,
        entity_name2index: dict[str, int],
        comparisons: Comparisons, # key_names == ["left_name, right_name"]
        init_multiscores : MultiScore, # key_names == "entity_name"
    ) -> npt.NDArray:
        """ Computes the scores given comparisons """
        entity_ordered_comparisons = comparisons.order_by_entities()
        def get_derivative_args(entity_index: int, solution: np.ndarray):
            entity_name = entities.iloc[entity_index].name
            values = dict()
            for row in entity_ordered_comparisons[entity_name]:
                values[ entity_name2index[row["with"]] ] = row["comparison"] / row["comparison_max"]
            indices = np.array(list(values.keys()), dtype=int)
            comparison_values = np.array(list(values.values()))
            return solution[indices], comparison_values

        return coordinate_descent(
            self.update_coordinate_function,
            get_args=get_derivative_args,
            initialization=self.init_scores(entity_name2index, init_multiscores),
            error=self.convergence_error,
        )        
    
    def user_learn_criterion(self, 
        entities: Entities,
        comparisons: Comparisons, # key_names == ["left_name, right_name"]
        init_multiscores: MultiScore, # key_names == ["entity_name"]
    ) -> dict[str, Score]:
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
        scores: np.ndarray,
    ) -> tuple[np.ndarray, np.ndarray]:
        
        comparisons_df = comparisons.to_df()
        left_indices = comparisons_df["left_name"].map(entity_name2index)
        right_indices = comparisons_df["right_name"].map(entity_name2index)
        score_diff = scores[left_indices] - scores[right_indices]
        comparisons_np = (comparisons_df["comparison"] / comparisons_df["comparison_max"]).to_numpy()
        score_log_likelihood = self.log_likelihood_function(score_diff, comparisons_np)
        
        brentq_kwargs = dict(
            f=self.translated_negative_log_likelihood,
            xtol=1e-2,
            extend_bounds="no",
        )

        lefts = np.empty_like(scores)
        rights = np.empty_like(scores)
        for i in range(len(scores)):
            brentq_kwargs["args"] = (
                score_diff, 
                comparisons_np, 
                score_log_likelihood,
                (1 *(left_indices == i) - 1 *(right_indices == i)).to_numpy()
            )             
            try:
                lefts[i] = -1 * njit_brentq(a=-self.max_uncertainty, b=0.0, **brentq_kwargs)
            except ValueError:
                lefts[i] = self.max_uncertainty

            try:
                rights[i] = njit_brentq(a=0.0, b=self.max_uncertainty, **brentq_kwargs)
            except ValueError:
                rights[i] = self.max_uncertainty
                
        return lefts, rights

    @cached_property
    def translated_negative_log_likelihood(self):
        """This function is a convex negative log likelihood, translated such
        that its minimum has a constant negative value at `delta=0`. The
        roots of this function are used to compute the uncertainties
        intervals. If it has only a single root, then uncertainty on the
        other side is considered infinite.
        """
        log_likelihood_function = self.log_likelihood_function
        high_likelihood_range_threshold = self.high_likelihood_range_threshold

        @njit
        def f(delta, score_diffs, comparison_values, score_log_likelihood, indicators):
            return (
                log_likelihood_function(score_diffs + delta * indicators, comparison_values)
                - score_log_likelihood
                - high_likelihood_range_threshold
            )

        return f

    @cached_property
    def update_coordinate_function(self):
        xtol = self.convergence_error / 10
        partial_derivative = self.partial_derivative

        @njit
        def f(derivative_args, old_coordinate_value):
            return njit_brentq(
                partial_derivative,
                args=derivative_args,
                xtol=xtol,
                a=old_coordinate_value - 1,
                b=old_coordinate_value + 1
            )
        return f

    @cached_property
    def partial_derivative(self):
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
            value: float,
            current_solution: npt.NDArray,
            comparisons_values: npt.NDArray,
        ) -> npt.NDArray:
            score_diff = value - current_solution
            return (value / prior_var) + np.sum(cfg_deriv(score_diff) - comparisons_values)
        
        return njit_partial_derivative


class UniformGBT(GeneralizedBradleyTerry):
    def __init__(
        self,
        prior_std_dev: float = 7.0,
        convergence_error: float = 1e-5,
        cumulant_generating_function_error: float = 1e-5,
        high_likelihood_range_threshold: float = 1.0,
        max_uncertainty: float=1e3,
    ):
        """

        Parameters (TODO)
        ----------
        """
        super().__init__(
            prior_std_dev=prior_std_dev,
            convergence_error=convergence_error,
            high_likelihood_range_threshold=high_likelihood_range_threshold,
            max_uncertainty=max_uncertainty
        )
        self.cumulant_generating_function_error = cumulant_generating_function_error

    @cached_property
    def log_likelihood_function(self):
        @njit
        def f(score_diff, r):
            score_diff_abs = np.abs(score_diff)
            return (
                np.where(
                    score_diff_abs > 1e-1,
                    np.where(
                        score_diff_abs < 20.0,
                        np.log(np.sinh(score_diff) / score_diff),
                        score_diff_abs - np.log(2) - np.log(score_diff_abs),
                    ),
                    score_diff_abs ** 2 / 6 - score_diff_abs ** 4 / 180,
                )
                + r * score_diff
            ).sum()

        return f

    @cached_property
    def cumulant_generating_function_derivative(self) -> Callable[[npt.NDArray], npt.NDArray]:
        tolerance = self.cumulant_generating_function_error

        @njit
        def f(score_diff: npt.NDArray):
            return np.where(
                np.abs(score_diff) < tolerance,
                score_diff / 3,
                1 / np.tanh(score_diff) - 1 / score_diff,
            )

        return f
