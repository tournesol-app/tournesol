from abc import abstractmethod
from typing import Optional

import pandas as pd
import numpy as np

try:
    import torch
except ImportError as exc:
    raise RuntimeError(
        "Using LBFGS requires 'torch' to be installed. "
        "Install 'solidago[torch]' to get the optional dependencies."
    ) from exc

from solidago.scoring_model import ScoringModel, DirectScoringModel
from .comparison_learning import ComparisonBasedPreferenceLearning


class LBFGSGeneralizedBradleyTerry(ComparisonBasedPreferenceLearning):
    def __init__(
        self,
        prior_std_dev: float = 7,
        convergence_error: float = 1e-5,
        n_steps: int = 3,
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
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @abstractmethod
    def cumulant_generating_function(self, score_diff: torch.Tensor) -> torch.Tensor:
        """The beauty of the generalized Bradley-Terry model is that it suffices
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
        """We estimate uncertainty by the flatness of the negative log likelihood,
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
        initialization: Optional[ScoringModel] = None,
        updated_entities: Optional[set[int]] = None,
    ) -> ScoringModel:
        """Learns only based on comparisons

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
        if len(comparisons) == 0:
            return DirectScoringModel()

        entities = list(set(comparisons["entity_a"]) | set(comparisons["entity_b"]))
        entity_coordinates = {entity: c for c, entity in enumerate(entities)}
        comparisons = (
            comparisons
            .assign(
                entity_a=comparisons["entity_a"].map(entity_coordinates),
                entity_b=comparisons["entity_b"].map(entity_coordinates),
                comparison=comparisons["comparison"] / comparisons["comparison_max"],
                pair=comparisons.apply(lambda c: {c["entity_a"], c["entity_b"]}, axis=1),
            )
            .drop_duplicates("pair", keep="last")
            .drop(columns="pair")
        )

        solution = torch.normal(
            0, 1, (len(entities),), requires_grad=True, dtype=float, device=self.device
        )
        for (entity, coord) in entity_coordinates.items():
            if initialization is not None and entity in initialization:
                solution[coord] = initialization[entity]

        lbfgs = torch.optim.LBFGS((solution,))

        def closure():
            lbfgs.zero_grad()
            loss = self.loss(solution, comparisons)
            loss.backward()
            return loss

        for _step in range(self.n_steps):
            lbfgs.step(closure)

        uncertainties = [
            self.hessian_diagonal_element(entity, solution, comparisons)
            for entity in range(len(entities))
        ]

        model = DirectScoringModel()
        for coordinate in range(len(solution)):
            model[entities[coordinate]] = (
                solution[coordinate].detach().numpy(),
                uncertainties[coordinate],
            )
        return model
        
    def loss(self, solution, comparisons) -> torch.Tensor:
        score_diff = (
            solution[comparisons["entity_b"].to_numpy()] 
            - solution[comparisons["entity_a"].to_numpy()]
        )
        return (
            torch.sum(solution**2) / (2 * self.prior_std_dev**2)
            + self.cumulant_generating_function(score_diff).sum()
            - (score_diff * torch.from_numpy(comparisons["comparison"].to_numpy())).sum()
        )
    
    def hessian_diagonal_element(
        self,
        entity: int,
        solution: torch.Tensor,
        comparisons: pd.DataFrame,
    ) -> float:
        """Computes the second partial derivative"""
        result = 1 / self.prior_std_dev**2
        c = comparisons[(comparisons["entity_a"] == entity) | (comparisons["entity_b"] == entity)]
        for row in c.itertuples():
            score_diff = (
                solution[row.entity_b]
                - solution[row.entity_a]
            )
            result += self.cumulant_generating_function_second_derivative(score_diff.detach())
        return result


class LBFGSUniformGBT(LBFGSGeneralizedBradleyTerry):
    def __init__(
        self,
        prior_std_dev: float = 7,
        comparison_max: float = 10,
        convergence_error: float = 1e-5,
        cumulant_generating_function_error: float = 1e-5,
        n_steps: int = 3,
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

    def cumulant_generating_function(self, score_diff: torch.Tensor) -> torch.Tensor:
        """For.

        Parameters
        ----------
        score_diff: float
            Score difference

        Returns
        -------
        out: float
        """
        return torch.where(
            score_diff != 0,
            torch.log(torch.sinh(score_diff) / score_diff),
            0.0
        )

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
        """We estimate uncertainty by the flatness of the negative log likelihood,
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
            return (1 / 3) - (score_diff**2 / 15)
        return 1 - (1 / np.tanh(score_diff) ** 2) + (1 / score_diff**2)

    def to_json(self):
        return type(self).__name__, dict(
            prior_std_dev=self.prior_std_dev,
            comparison_max=self.comparison_max,
            convergence_error=self.convergence_error,
            cumulant_generating_function_error=self.cumulant_generating_function_error,
        )

    def __str__(self):
        prop_names = [
            "prior_std_dev",
            "convergence_error",
            "comparison_max",
            "cumulant_generating_function_error",
            "n_steps",
        ]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"
