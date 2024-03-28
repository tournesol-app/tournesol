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
        prior_std_dev: float=7,
        convergence_error: float=1e-5,
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
    
    @property
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
        raise NotImplementedError
    
    @abstractmethod
    def cumulant_generating_function_second_derivative(self, score_diff: float) -> float:
        """ We estimate uncertainty by the flatness of the negative log likelihood,
        which is directly given by the second derivative of the cumulant generating function.
        
        Parameters
        ----------
        score_diff: float
            Score difference
            
        Returns
        -------
        out: float
        """
        pass

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
            for (entity_id, entity_coord) in entity_coordinates.items():
                entity_init_values = initialization(entity_id)
                if entity_init_values is not None:
                    init_solution[entity_coord] = entity_init_values[0]
        
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
        
        uncertainties = [ 
            self.hessian_diagonal_element(coordinate, solution, comparisons_dict[coordinate][0])
            for coordinate in range(len(entities))
        ]
        
        model = DirectScoringModel()
        for coordinate in range(len(solution)):
            model[entities[coordinate]] = solution[coordinate], uncertainties[coordinate]
        
        return model
        
    def comparisons_dict(self, comparisons, entity_coordinates) -> dict[int, tuple[npt.NDArray, npt.NDArray]]:
        comparisons = (
            comparisons[
                ["entity_a","entity_b","comparison", "comparison_max"]
            ]
            .assign(
                pair=comparisons.apply(lambda c: {c["entity_a"], c["entity_b"]}, axis=1)
            )
            .drop_duplicates("pair", keep="last")
            .drop(columns="pair")
        )
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
    
    def hessian_diagonal_element(
        self, 
        coordinate: int,
        solution: np.ndarray,
        comparisons_indices: np.ndarray,
    ) -> float:
        """ Computes the second partial derivative """
        result = 1 / self.prior_std_dev ** 2
        for coordinate_bis in comparisons_indices:
            score_diff = solution[coordinate] - solution[coordinate_bis]
            result += self.cumulant_generating_function_second_derivative(score_diff)
        return result
    
        
class UniformGBT(GeneralizedBradleyTerry):
    def __init__(
        self, 
        prior_std_dev: float=7,
        comparison_max: float=10,
        convergence_error: float=1e-5,
        cumulant_generating_function_error: float=1e-5,
    ):
        """
        
        Parameters
        ----------
        initialization: dict[int, float]
            previously computed entity scores
        error: float
            tolerated error
        """
        super().__init__(prior_std_dev, convergence_error)
        self.comparison_max = comparison_max
        self.cumulant_generating_function_error = cumulant_generating_function_error
    
    @cached_property
    def cumulant_generating_function_derivative(self) -> Callable[[npt.NDArray], npt.NDArray]:
        """ For.
        
        Parameters
        ----------
        score_diff: float
            Score difference
            
        Returns
        -------
        out: float
        """
        tolerance = self.cumulant_generating_function_error

        @njit
        def f(score_diff: npt.NDArray):
            return np.where(
                np.abs(score_diff) < tolerance,
                score_diff / 3,
                1/ np.tanh(score_diff) - 1 / score_diff
            )
        return f

    
    def cumulant_generating_function_second_derivative(self, score_diff: float) -> float:
        """ We estimate uncertainty by the flatness of the negative log likelihood,
        which is directly given by the second derivative of the cumulant generating function.
        
        Parameters
        ----------
        score_diff: float
            Score difference
            
        Returns
        -------
        out: float
        """
        if np.abs(score_diff) < self.cumulant_generating_function_error:
            return (1/3) - (score_diff**2 / 15)
        return 1 - (1 / np.tanh(score_diff)**2) + (1 / score_diff**2)
    
    def to_json(self):
        return type(self).__name__, dict(
            prior_std_dev=self.prior_std_dev,
            comparison_max=self.comparison_max,
            convergence_error=self.convergence_error,
            cumulant_generating_function_error=self.cumulant_generating_function_error,
        )
    
    def __str__(self):
        prop_names = ["prior_std_dev", "convergence_error", "comparison_max", 
            "cumulant_generating_function_error"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"
