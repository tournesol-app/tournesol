from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import numpy as np
import torch

from solidago.scoring_model import ScoringModel, DirectScoringModel
from solidago.solvers.optimize import coordinate_descent

from .comparison_learning import ComparisonBasedPreferenceLearning


class LBFGSGeneralizedBradleyTerry(ComparisonBasedPreferenceLearning):
    def __init__(
        self, 
        prior_std_dev: float=7,
        convergence_error: float=1e-5,
        n_steps: int=5,
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
        self.n_steps = n_steps
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    
    @abstractmethod
    def cumulant_generating_function(self, score_diff: float) -> float:
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
        
        solution = torch.normal(0, 1, (len(entities),), requires_grad=True, dtype=float, 
            device=self.device)
        for entity in entity_coordinates:
            if initialization is not None and entity in initialization:
                solution[entity_coordinates[entity]] = initialization[entity]        
        
        lbfgs = torch.optim.LBFGS((solution,))
        def closure():
            lbfgs.zero_grad()
            loss = self.loss(solution, comparisons, entity_coordinates)
            loss.backward()
            return loss
        
        for step in range(self.n_steps):
            loss = self.loss(solution, comparisons, entity_coordinates)
            lbfgs.step(closure)
        
        uncertainties = [ 
            self.hessian_diagonal_element(entity, solution, comparisons, entity_coordinates) 
            for entity in entities
        ]
        
        model = DirectScoringModel()
        for coordinate in range(len(solution)):
            model[entities[coordinate]] = (
                solution[coordinate].detach().numpy(), 
                uncertainties[coordinate]
            )
        
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
        
    def loss(self, solution, comparisons, entity_coordinates):
        loss = torch.sum(solution**2) / (2 * self.prior_std_dev**2)
        for _, row in comparisons.iterrows():
            score_diff = solution[entity_coordinates[row["entity_b"]]] \
                - solution[entity_coordinates[row["entity_a"]]]
            loss += self.cumulant_generating_function(score_diff) 
            loss -= row["comparison"] * score_diff / row["comparison_max"]
        return loss
    
    def hessian_diagonal_element(
        self, 
        entity: int, 
        solution: np.array, 
        comparisons: pd.DataFrame, 
        entity_coordinates: dict[int, int],
    ) -> float:
        """ Computes the second partial derivative """
        result = 1 / self.prior_std_dev ** 2
        c = comparisons[(comparisons["entity_a"] == entity) | (comparisons["entity_b"] == entity)]
        for _, row in c.iterrows():
            score_diff = solution[entity_coordinates[row["entity_b"]]] \
                - solution[entity_coordinates[row["entity_a"]]]
            result += self.cumulant_generating_function_second_derivative(score_diff.detach())
        return result.detach().numpy()
    
        
class LBFGSUniformGBT(LBFGSGeneralizedBradleyTerry):
    def __init__(
        self, 
        prior_std_dev: float=7,
        comparison_max: float=10,
        convergence_error: float=1e-5,
        cumulant_generating_function_error: float=1e-5,
        n_steps: int=5,
    ):
        """
        
        Parameters
        ----------
        initialization: dict[int, float]
            previously computed entity scores
        error: float
            tolerated error
        """
        super().__init__(prior_std_dev, convergence_error, n_steps)
        self.comparison_max = comparison_max
        self.cumulant_generating_function_error = cumulant_generating_function_error
    
    def cumulant_generating_function(self, score_diff: float) -> float:
        """ For.
        
        Parameters
        ----------
        score_diff: float
            Score difference
            
        Returns
        -------
        out: float
        """
        if score_diff == 0:
            return 0
        return torch.log(torch.sinh(score_diff) / score_diff)
    
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
    
    def to_json(self):
        return type(self).__name__, dict(
            prior_std_dev=self.prior_std_dev,
            comparison_max=self.comparison_max,
            convergence_error=self.convergence_error,
            cumulant_generating_function_error=self.cumulant_generating_function_error,
        )
    
    def __str__(self):
        prop_names = ["prior_std_dev", "convergence_error", "comparison_max", 
            "cumulant_generating_function_error", "n_steps"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"
