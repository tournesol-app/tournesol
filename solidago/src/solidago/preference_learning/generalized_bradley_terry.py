from abc import abstractmethod
from functools import cached_property
from typing import Optional, Callable

import pandas as pd
import numpy as np
import numpy.typing as npt
from numba import njit

from solidago.scoring_model import ScoringModel, DirectScoringModel
from solidago.solvers.optimize import coordinate_descent, njit_brentq

from .comparison_learning import ComparisonBasedPreferenceLearning


class GeneralizedBradleyTerry(ComparisonBasedPreferenceLearning):
    def __init__(
        self, 
        prior_std_dev: float=7.0,
        convergence_error: float=1e-5,
        high_likelihood_range_threshold = 1.0,
    ):
        """
        
        Parameters
        ----------
        initialization: dict[int, float]
            previously computed entity scores
        error: float
            tolerated error
        """
        self.prior_std_dev = prior_std_dev
        self.convergence_error = convergence_error
        self.high_likelihood_range_threshold = high_likelihood_range_threshold

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

    def comparison_learning(
        self, 
        comparisons: pd.DataFrame, 
        entities=None, 
        initialization: Optional[ScoringModel]=None,
        updated_entities: Optional[set[int]]=None,
    ) -> ScoringModel:
        """ Learns only based on comparisons
        
        Parameters
        ----------
        comparisons: DataFrame with columns
            * entity_a: int
            * entity_b: int
            * comparison: float
            * comparison_max: float
        entities: DataFrame
            This parameter is not used
        """
        entities = list(set(comparisons["entity_a"]) | set(comparisons["entity_b"]))
        entity_coordinates = { entity: c for c, entity in enumerate(entities) }

        comparisons_dict = self.comparisons_dict(comparisons, entity_coordinates)

        init_solution = np.zeros(len(entities))
        if initialization is not None:
            for (entity_id, model_values) in initialization.iter_entities():
                entity_coord = entity_coordinates.get(entity_id)
                if entity_coord is not None:
                    init_solution[entity_coord] = model_values[0]

        updated_coordinates = list() if updated_entities is None else [
            entity_coordinates[entity] for entity in updated_entities
        ]

        def get_derivative_args(coord: int, sol: np.ndarray):
            indices, comparisons_bis = comparisons_dict[coord]
            return (
                sol[indices],
                comparisons_bis
            )

        solution = coordinate_descent(
            self.update_coordinate_function,
            get_args=get_derivative_args,
            initialization=init_solution,
            updated_coordinates=updated_coordinates,
            error=self.convergence_error,
        )

        comparisons = comparisons.assign(
            entity_a_coord=comparisons["entity_a"].map(entity_coordinates),
            entity_b_coord=comparisons['entity_b'].map(entity_coordinates),
        )
        score_diff = solution[comparisons["entity_a_coord"]] - solution[comparisons["entity_b_coord"]]
        r_actual = (comparisons["comparison"] / comparisons["comparison_max"]).to_numpy()

        uncertainties_left = np.empty_like(solution)
        uncertainties_right = np.empty_like(solution)
        ll_actual = self.log_likelihood_function(score_diff, r_actual)

        for coordinate in range(len(solution)):
            comparison_indicator = (
                (comparisons["entity_a_coord"] == coordinate).astype(int)
                - (comparisons["entity_b_coord"] == coordinate).astype(int)
            ).to_numpy()
            try:
                uncertainties_left[coordinate] = -1 * njit_brentq(
                    self.translated_negative_log_likelihood,
                    args=(score_diff, r_actual, comparison_indicator, ll_actual),
                    xtol=1e-2,
                    a=-self.MAX_UNCERTAINTY,
                    b=0.0,
                    extend_bounds="no",
                )
            except ValueError:
                uncertainties_left[coordinate] = self.MAX_UNCERTAINTY

            try:
                uncertainties_right[coordinate] = njit_brentq(
                    self.translated_negative_log_likelihood,
                    args=(score_diff, r_actual, comparison_indicator, ll_actual),
                    xtol=1e-2,
                    a=0.0,
                    b=self.MAX_UNCERTAINTY,
                    extend_bounds="no",
                )
            except ValueError:
                uncertainties_right[coordinate] = self.MAX_UNCERTAINTY

        model = DirectScoringModel()
        for coord in range(len(solution)):
            model[entities[coord]] = solution[coord], uncertainties_left[coord], uncertainties_right[coord]
        return model

    def comparisons_dict(self, comparisons, entity_coordinates) -> dict[int, tuple[npt.NDArray, npt.NDArray]]:
        comparisons = comparisons[["entity_a","entity_b","comparison", "comparison_max"]]
        comparisons_sym = pd.concat(
            [
                comparisons,
                 pd.DataFrame(
                    {
                        "entity_a": comparisons.entity_b,
                        "entity_b": comparisons.entity_a,
                        "comparison": -1 * comparisons.comparison,
                        "comparison_max": comparisons.comparison_max,
                    }
                ),
            ]
        )
        comparisons_sym.entity_a = comparisons_sym.entity_a.map(entity_coordinates)
        comparisons_sym.entity_b = comparisons_sym.entity_b.map(entity_coordinates)
        comparisons_sym.comparison = -1 * np.where(
            np.isfinite(comparisons_sym.comparison_max),
            comparisons_sym.comparison / comparisons_sym.comparison_max,
            comparisons_sym.comparison
        )
        return {
            coord: (group["entity_b"].to_numpy(),  group["comparison"].to_numpy())
            for (coord, group) in comparisons_sym.groupby("entity_a")
        }  # type: ignore

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

    def to_json(self):
        return type(self).__name__, dict(
            prior_std_dev=self.prior_std_dev,
            convergence_error=self.convergence_error,
            cumulant_generating_function_error=self.cumulant_generating_function_error,
            high_likelihood_range_threshold=self.high_likelihood_range_threshold,
        )

    def __str__(self):
        prop_names = ["prior_std_dev", "convergence_error", "cumulant_generating_function_error"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"
