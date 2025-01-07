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

from solidago._state import *
from solidago.primitives import dichotomy
from .base import PreferenceLearning


class LBFGSGeneralizedBradleyTerry(PreferenceLearning):
    def __init__(self,
        prior_std_dev: float=7,
        convergence_error: float=1e-5,
        high_likelihood_range_threshold: float=1.0,
        max_uncertainty: float=1e3,
        max_iter: int=100,
    ):
        """ Generalized Bradley Terry is a class of porbability models of comparisons,
        introduced in the paper "Generalized Bradley-Terry Models for Score Estimation 
        from Paired Comparisons" by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang
        and Oscar Villemaud, and published at AAAI'24.
        
        This implementation leverages the pytorch implementation of the Limited-memory 
        Broyden-Fletcher-Goldfarb-Shanno (LBFGS) algorithm, a second-order quasi-Newton 
        method with limited demands of computer memory.

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
        max_iter: int=100
            Maximal number of iterations used
        """
        self.prior_std_dev = prior_std_dev
        self.convergence_error = convergence_error
        self.high_likelihood_range_threshold = high_likelihood_range_threshold
        self.max_uncertainty = max_uncertainty
        self.max_iter = max_iter
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    @abstractmethod
    def cumulant_generating_function(self, score_diff: torch.Tensor) -> torch.Tensor:
        """The beauty of the generalized Bradley-Terry model is that it suffices
        to specify its cumulant generating function derivative to fully define it,
        and to allow a fast computation of its corresponding maximum a posterior.

        Parameters
        ----------
        score_diff: torch.Tensor
            Score differences

        Returns
        -------
        out: torch.Tensor
            values of the cumulant generating function on the score differences
        """
        pass

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
    ) -> torch.Tensor:
        scores = torch.zeros(len(entity_names))
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
    ) -> torch.Tensor:
        """ Computes the scores given comparisons """
        comparisons_df = comparisons.to_df().assign(
            left_index=comparisons["left_name"].map(entity_name2index),
            right_index=comparisons['right_name'].map(entity_name2index),
            normalized_comparisons=(comparisons['comparison'] / comparisons['comparison_max'])
        )
        solution = self.init_solution(direct_scoring, entity_names, entity_name2index)
        solution.requires_grad = True
        solution = solution.to(self.device)

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
        return solution
            
    def user_learn_criterion(self, 
        user: User,
        comparisons: Comparisons,
        direct_scoring: DirectScoring
    ) -> dict[str, Score]:
        if len(comparisons) == 0:
            return DirectScoringModel()

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

            model[entity_names[coordinate]] = (
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
