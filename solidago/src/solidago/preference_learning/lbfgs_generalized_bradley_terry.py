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
from solidago.solvers import dichotomy
from .comparison_learning import ComparisonBasedPreferenceLearning

class LBFGSGeneralizedBradleyTerry(ComparisonBasedPreferenceLearning):
    def __init__(
        self,
        prior_std_dev: float = 7,
        convergence_error: float = 1e-5,
        max_iter: int = 100,
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
        self.max_iter = max_iter
        self.high_likelihood_range_threshold = high_likelihood_range_threshold
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
        comparisons_np = (
            comparisons["entity_a"].map(entity_coordinates).to_numpy(),
            comparisons["entity_b"].map(entity_coordinates).to_numpy(),
            (comparisons["comparison"] / comparisons["comparison_max"]).to_numpy()
        )

        solution = np.random.normal(0.0, 1.0, size=len(entities))
        if initialization is not None:
            for (entity_id, values) in initialization.iter_entities():
                entity_coord = entity_coordinates.get(entity_id)
                if entity_coord is not None:
                    score, _left, _right = values
                    solution[entity_coord] = score

        solution = torch.tensor(solution, requires_grad=True, device=self.device)
        lbfgs = torch.optim.LBFGS(
            (solution,),
            max_iter=self.max_iter,
            tolerance_change=self.convergence_error,
            line_search_fn="strong_wolfe",
        )

        def closure():
            lbfgs.zero_grad()
            loss = self.loss(solution, comparisons_np)
            loss.backward()
            return loss

        lbfgs.step(closure)  # type: ignore

        n_iter = lbfgs.state_dict()["state"][0]["n_iter"]
        if n_iter >= self.max_iter:
            raise RuntimeError(f"LBFGS failed to converge in {n_iter} iterations")

        solution = solution.detach()
        if solution.isnan().any():
            raise RuntimeError(f"Nan in solution, state: {lbfgs.state_dict()}")

        def loss_with_delta(delta, comparisons, coord):
            solution_with_delta = solution.clone()
            solution_with_delta[coord] += delta
            return self.loss(solution_with_delta, comparisons, with_regularization=False).item()

        model = DirectScoringModel()
        for coordinate in range(len(solution)):
            mask = ((comparisons_np[0] == coordinate) | (comparisons_np[1] == coordinate))
            comparisons_np_subset = tuple(arr[mask] for arr in comparisons_np)
            ll_solution = self.loss(solution, comparisons_np_subset, with_regularization=False).item()

            try:
                uncertainty_left = -1 * dichotomy.solve(
                    loss_with_delta,
                    value=ll_solution + self.high_likelihood_range_threshold,
                    args=(comparisons_np_subset, coordinate),
                    xmin=-self.MAX_UNCERTAINTY,
                    xmax=0.0,
                    error=1e-1,
                )
            except ValueError:
                uncertainty_left = self.MAX_UNCERTAINTY

            try:
                uncertainty_right = dichotomy.solve(
                    loss_with_delta,
                    value=ll_solution + self.high_likelihood_range_threshold,
                    args=(comparisons_np_subset, coordinate),
                    xmin=0.0,
                    xmax=self.MAX_UNCERTAINTY,
                    error=1e-1,
                )
            except ValueError:
                uncertainty_right = self.MAX_UNCERTAINTY

            model[entities[coordinate]] = (
                solution[coordinate].item(),
                uncertainty_left,
                uncertainty_right,
            )
        return model

    def loss(self, solution, comparisons, with_regularization=True):
        comp_a, comp_b, comp_value = comparisons
        score_diff = solution[comp_b] - solution[comp_a]
        loss = (
            self.cumulant_generating_function(score_diff).sum()
            - (score_diff * torch.from_numpy(comp_value)).sum()
        )
        if with_regularization:
            loss += torch.sum(solution**2) / (2 * self.prior_std_dev**2)
        return loss


class LBFGSUniformGBT(LBFGSGeneralizedBradleyTerry):
    def __init__(
        self,
        prior_std_dev: float = 7,
        convergence_error: float = 1e-5,
        cumulant_generating_function_error: float = 1e-5,
        max_iter: int = 100,
        high_likelihood_range_threshold: float = 1.0,
    ):
        """
        Parameters (TODO)
        ----------
        """
        super().__init__(
            prior_std_dev,
            convergence_error,
            max_iter=max_iter,
            high_likelihood_range_threshold=high_likelihood_range_threshold,
        )
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
        score_diff_abs = score_diff.abs()
        return torch.where(
            score_diff_abs > 1e-1,
            torch.where(
                score_diff_abs < 20.0,
                (torch.sinh(score_diff) / score_diff).log(),
                score_diff_abs - np.log(2) - score_diff_abs.log(),
            ),
            score_diff_abs ** 2 / 6 - score_diff_abs ** 4 / 180,
        )

    def to_json(self):
        return type(self).__name__, dict(
            prior_std_dev=self.prior_std_dev,
            convergence_error=self.convergence_error,
            cumulant_generating_function_error=self.cumulant_generating_function_error,
            high_likelihood_range_threshold=self.high_likelihood_range_threshold,
        )

    def __str__(self):
        prop_names = [
            "prior_std_dev",
            "convergence_error",
            "cumulant_generating_function_error",
            "max_iter",
        ]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"
