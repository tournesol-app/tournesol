from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import numpy as np

from solidago.scoring_model import ScoringModel, DirectScoringModel
from solidago.solvers.optimize import coordinate_descent

from .base import ComparisonBasedPreferenceLearning


class GeneralizedBradleyTerry(ComparisonBasedPreferenceLearning):
    def __init__(
        self, 
        prior_std_dev: float=7,
        initialization: dict[int, float]=dict(),
        convergence_error: float=1e-5                    
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
    
    @abstractmethod
    def cumulant_generating_function_derivative(self, score_diff: float) -> float:
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
        pass
    
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

    def comparison_learning(
        self, 
        comparisons: pd.DataFrame, 
        entities=None, 
        initialization: Optional[ScoringModel] = None
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
        for entity in entity_coordinates:
            if initialization is not None and entity in initialization:
                init_solution[entity_coordinates[entity]] = initialization[entity]        
        
        def loss_partial_derivative(coordinate, value, solution): 
            return self.partial_derivative(coordinate, value, solution, 
                comparisons_dict[coordinate])
        
        solution = coordinate_descent(
            loss_partial_derivative = loss_partial_derivative,
            initialization = init_solution,
            error = self.convergence_error
        )
        
        uncertainties = [ 
            self.hessian_diagonal_element(coordinate, solution, comparisons_dict[coordinate]) 
            for coordinate in range(len(entities))
        ]
        
        model = DirectScoringModel()
        for coordinate in range(len(solution)):
            model[entities[coordinate]] = solution[coordinate], uncertainties[coordinate]
        
        return model
        
    def comparisons_dict(self, comparisons, entity_coordinates):
        comparisons_dict = { entity: dict() for entity in entity_coordinates.values() }
        
        for _, row in comparisons.iterrows():
            
            a = entity_coordinates[row["entity_a"]]
            b = entity_coordinates[row["entity_b"]]
            
            comparison = row["comparison"]
            if np.isfinite(row["comparison_max"]):
                comparison /= row["comparison_max"]
            
            comparisons_dict[a][b] = - comparison
            comparisons_dict[b][a] = comparison
            
        return comparisons_dict
            
    def partial_derivative(
        self, 
        coordinate: int, 
        value: float,
        solution: np.array, 
        comparisons_dict: dict[int, float]
    ) -> float:
        """ Computes the partial derivative along a coordinate, 
        for a given value along the coordinate,
        when other coordinates' values are given by the solution.
        The computation evidently depends on the dataset,
        which is given by coordinate_comparisons.
        """
        result = value / self.prior_std_dev ** 2
        for coordinate_bis in comparisons_dict:
            score_diff = value - solution[coordinate_bis]
            result += self.cumulant_generating_function_derivative(score_diff)
            result -= comparisons_dict[coordinate_bis]
        return result
    
    def hessian_diagonal_element(
        self, 
        coordinate: int, 
        solution: np.array, 
        comparisons_dict: dict[int, float]
    ) -> float:
        """ Computes the second partial derivative """
        result = 1 / self.prior_std_dev ** 2
        for coordinate_bis in comparisons_dict:
            score_diff = solution[coordinate] - solution[coordinate_bis]
            result += self.cumulant_generating_function_second_derivative(score_diff)
        return result
    
        
class UniformGBT(GeneralizedBradleyTerry):
    def __init__(
        self, 
        prior_std_dev: float=7,
        comparison_max: float=10,
        initialization: dict[int, float]=dict(),
        convergence_error: float=1e-5,
        cumulant_generating_function_error: float=1e-5
    ):
        """
        
        Parameters
        ----------
        initialization: dict[int, float]
            previously computed entity scores
        error: float
            tolerated error
        """
        super().__init__(prior_std_dev, initialization, convergence_error)
        self.comparison_max = comparison_max
        self.cumulant_generating_function_error = cumulant_generating_function_error
    
    def cumulant_generating_function_derivative(self, score_diff: float) -> float:
        """ For.
        
        Parameters
        ----------
        score_diff: float
            Score difference
            
        Returns
        -------
        out: float
        """
        if np.abs(score_diff) < self.cumulant_generating_function_error:
            return score_diff / 3
        return 1 / np.tanh(score_diff) - 1 / score_diff
    
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
    
    
