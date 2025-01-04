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
    def __init__(
        self, 
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

    @cached_property
    def translated_negative_log_likelihood(self):
        """This function is a convex negative log likelihood, translated such
        that its minimum has a constant negative value at `delta=0`. The
        roots of this function are used to compute the uncertainties
        intervals. If it has only a single root, then uncertainty on the
        other side is considered infinite.
        """
        ll_function = self.log_likelihood_function
        high_likelihood_range_threshold = self.high_likelihood_range_threshold

        @njit
        def f(delta, theta_diff, r, coord_indicator, ll_actual):
            return (
                ll_function(theta_diff + delta * coord_indicator, r)
                - ll_actual
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

    def user_learn(self, 
        user: User,
        entities: Entities,
        assessments: Assessments,
        comparisons: Comparisons,
        base_model: BaseModel,
    ) -> BaseModel:
        """ Learns only based on comparisons """
        model = DirectScoring()
        direct_scoring = base_model.to_direct(entities)
        reordered_direct_scoring = direct_scoring.reorder_keys(["criterion", "entity_name"])
        for criterion in comparisons.get_set("criterion", "default"):
            entity_scores = self.user_learn_criterion(
                user, 
                reordered_comparisons[{"criterion": criterion }], 
                reordered_direct_scoring[criterion]
            )
            for index, (entity_name, score) in enumerate(entity_scores.items()):
                model[entity_name].add_row(dict(criterion=criterion) | score.to_dict())
        return model

    def init_solution(self, 
        init_model: DirectScoring, 
        entity_names: list[str],
        entity_name2index: dict[str, int]
    ) -> np.ndarray:
        scores = np.zeros(len(entity_names))
        if initialization is not None:
            for index, entity_name in enumerate(entity_names):
                score = init_model(entity_name)
                if not score.isnan():
                    scores[index] = score.value
        return scores
    
    def compute_scores_without_uncertainties(self, 
        comparisons: Comparisons,
        direct_scoring: DirectScoring,
        entity_names: list[str],
        entity_name2index: dict[str, int],
    ) -> npt.NDArray:
        """ Computes the scores given comparisons """
        entity_ordered_comparisons = comparisons.order_by_entities()
        def get_derivative_args(entity_index: int, solution: np.ndarray):
            entity_name = entity_names[entity_index]
            df = entity_ordered_comparisons[entity_name].to_df()
            values = dict()
            for _, row in df.iterrows():
                values[ entity_name2index[row["with"]] ] = row["comparison"] / row["comparison_max"]
            values = list(zip(*values.values()))
            indices = np.array(list(values.keys()))
            comparison_values = np.array(list(values.values()))
            return solution[indices], comparison_values

        init_solution = self.init_solution(direct_scoring, entity_names, entity_name2index)
        return coordinate_descent(
            self.update_coordinate_function,
            get_args=get_derivative_args,
            initialization=init_solution,
            updated_coordinates=list(),
            error=self.convergence_error,
        )        
    
    def user_learn_criterion(self, 
        user: User,
        comparisons: Comparisons,
        direct_scoring: DirectScoring
    ) -> dict[str, Score]:
        """
        Returns
        -------
        out: dict
            out[entity_name] must be of type Score (i.e. with a value and left/right uncertainties
        """
        entity_names = list(comparisons.get_set("left_name") | comparisons.get_set("right_name"))
        entity_name2index = { entity_name: c for c, entity_name in enumerate(entity_names) }
        
        solution = self.compute_scores_without_uncertainties(
            comparisons, 
            direct_scoring, 
            entity_names, 
            entity_name2index
        )
        
        comparisons_df = comparisons.to_df().assign(
            left_index=comparisons["left_name"].map(entity_name2index),
            right_index=comparisons['right_name'].map(entity_name2index),
        )
        score_diff = solution[comparisons_df["left_index"]] - solution[comparisons_df["right_index"]]
        comparisons_np = (comparisons_df["comparison"] / comparisons_df["comparison_max"]).to_numpy()

        uncertainties_left = np.empty_like(solution)
        uncertainties_right = np.empty_like(solution)
        ll_actual = self.log_likelihood_function(score_diff, comparisons_np)

        for coordinate in range(len(solution)):
            comparison_indicator = (
                (comparisons["left_index"] == coordinate).astype(int)
                - (comparisons["right_index"] == coordinate).astype(int)
            ).to_numpy()
            try:
                uncertainties_left[coordinate] = -1 * njit_brentq(
                    self.translated_negative_log_likelihood,
                    args=(score_diff, r_actual, comparison_indicator, ll_actual),
                    xtol=1e-2,
                    a=-self.max_uncertainty,
                    b=0.0,
                    extend_bounds="no",
                )
            except ValueError:
                uncertainties_left[coordinate] = self.max_uncertainty

            try:
                uncertainties_right[coordinate] = njit_brentq(
                    self.translated_negative_log_likelihood,
                    args=(score_diff, r_actual, comparison_indicator, ll_actual),
                    xtol=1e-2,
                    a=0.0,
                    b=self.max_uncertainty,
                    extend_bounds="no",
                )
            except ValueError:
                uncertainties_right[coordinate] = self.max_uncertainty

        model = DirectScoringModel()
        for i in range(len(solution)):
            model[entity_names[i]] = solution[i], uncertainties_left[i], uncertainties_right[i]
        return model

    @cached_property
    def partial_derivative(self):
        """ Computes the partial derivative along a coordinate, 
        for a given value along the coordinate,
        when other coordinates' values are given by the solution.
        The computation evidently depends on the dataset,
        which is given by coordinate_comparisons.
        """
        prior_std_dev = self.prior_std_dev
        cumulant_generating_function_derivative = self.cumulant_generating_function_derivative

        @njit
        def njit_partial_derivative(
            value: float,
            current_solution: npt.NDArray,
            comparisons_values: npt.NDArray,
        ) -> npt.NDArray:
            score_diff = value - current_solution
            return (
                (value / prior_std_dev ** 2)
                + np.sum(
                    cumulant_generating_function_derivative(score_diff)
                    - comparisons_values
                )
            )
        return njit_partial_derivative


class UniformGBT(GeneralizedBradleyTerry):
    def __init__(
        self,
        prior_std_dev: float = 7.0,
        convergence_error: float = 1e-5,
        cumulant_generating_function_error: float = 1e-5,
        high_likelihood_range_threshold: float = 1.0,
    ):
        """

        Parameters (TODO)
        ----------
        """
        super().__init__(
            prior_std_dev,
            convergence_error,
            high_likelihood_range_threshold=high_likelihood_range_threshold
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
