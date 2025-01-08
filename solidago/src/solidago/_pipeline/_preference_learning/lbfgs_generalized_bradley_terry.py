from abc import abstractmethod
from typing import Optional

import pandas as pd
import numpy as np
import numpy.typing as npt

try:
    import torch
except ImportError as exc:
    raise RuntimeError(
        "Using LBFGS requires 'torch' to be installed. "
        "Install 'solidago[torch]' to get the optional dependencies."
    ) from exc

from solidago._state import *
from solidago.primitives import dichotomy
from .generalized_bradley_terry import GeneralizedBradleyTerry, UniformGBT


default_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class LBFGSGeneralizedBradleyTerry(GeneralizedBradleyTerry):
    def __init__(self,
        prior_std_dev: float=7,
        uncertainty_nll_increase: float=1.0,
        max_uncertainty: float=1e3,
        convergence_error: float=1e-5,
        max_iter: int=100,
        device: torch.device=default_device,
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
        super().__init__(
            prior_std_dev=prior_std_dev,
            uncertainty_nll_increase=uncertainty_nll_increase,
            max_uncertainty=max_uncertainty,
        )
        self.convergence_error = convergence_error
        self.max_iter = max_iter
        self.device = device

    @abstractmethod
    def cumulant_generating_function(self, score_diffs: torch.Tensor) -> torch.Tensor:
        """ To use the cumulant generating function in the context of pytorch,
        it is sufficent to write the cumulant generating function.
        This function must however be written as a torch function,
        i.e. with torch inputs and outputs.
        
        Parameters
        ----------
        score_diffs: torch.Tensor
            Score differences
            
        Returns
        -------
        cgf: torch.Tensor
            cgf[i] is the cumulant-generating function at score_diffs[i]
        """

    def compute_scores(self, 
        entities: Entities,
        entity_name2index: dict[str, int],
        comparisons: Comparisons, # key_names == ["left_name, right_name"]
        init_multiscores : MultiScore, # key_names == "entity_name"
    ) -> npt.NDArray:
        """ Computes the scores given comparisons """
        scores = self.init_scores(entity_name2index, init_multiscores)
        scores = torch.tensor(scores, dtype=torch.float64)
        scores.requires_grad = True
        scores = scores.to(self.device)

        lbfgs = torch.optim.LBFGS(
            (scores,),
            max_iter=self.max_iter,
            tolerance_change=self.convergence_error,
            line_search_fn="strong_wolfe",
        )
        
        def closure():
            lbfgs.zero_grad()
            loss = self.negative_log_posterior(scores, entities, entity_name2index, comparisons)
            loss.backward()
            return loss

        lbfgs.step(closure)  # type: ignore

        n_iter = lbfgs.state_dict()["state"][0]["n_iter"]
        if n_iter >= self.max_iter:
            raise RuntimeError(f"LBFGS failed to converge in {n_iter} iterations")

        scores = scores.detach()
        if scores.isnan().any():
            raise RuntimeError(f"Nan in solution, state: {lbfgs.state_dict()}")
        return np.array(scores)
            
    def negative_log_posterior(self, 
        scores: torch.Tensor,
        entities: Entities,
        entity_name2index: dict[str, int],
        comparisons: Comparisons,
    ) -> torch.Tensor:
        """ Negative log posterior """
        entity_indices = comparisons.compared_entity_indices(entity_name2index)
        score_diffs = scores[entity_indices["left"]] - scores[entity_indices["right"]]
        normalized_comparisons = comparisons.normalized_comparisons()
        loss = self.cumulant_generating_function(score_diffs).sum()
        loss -= (score_diffs * torch.tensor(normalized_comparisons)).sum()
        return loss + (scores**2).sum() / (2 * self.prior_std_dev**2)


class LBFGSUniformGBT(LBFGSGeneralizedBradleyTerry, UniformGBT):
    def __init__(self,
        prior_std_dev: float=7,
        uncertainty_nll_increase: float=1.0,
        max_uncertainty: float=1e3,
        convergence_error: float=1e-5,
        max_iter: int=100,
        device: torch.device=default_device,
    ):
        """
        Parameters (TODO)
        ----------
        """
        super().__init__(
            prior_std_dev=prior_std_dev,
            uncertainty_nll_increase=uncertainty_nll_increase,
            max_uncertainty=max_uncertainty,
            convergence_error=convergence_error,
            max_iter=max_iter,
            device=device,
        )

    def cumulant_generating_function(self, score_diffs: torch.Tensor) -> torch.Tensor:
        """ Vectorized cumulant generating function adapted for pytorch

        Parameters
        ----------
        score_diffs: torch.Tensor
            Score difference

        Returns
        -------
        cgf: torch.Tensor
            cfg[i] is the cgf of score_diff[i]
        """
        score_diffs_abs = score_diffs.abs()
        return torch.where(
            score_diffs_abs > 1e-1,
            torch.where(
                score_diffs_abs < 20.0,
                (torch.sinh(score_diffs) / score_diffs).log(),
                score_diffs_abs - np.log(2) - score_diffs_abs.log(),
            ),
            score_diffs_abs ** 2 / 6 - score_diffs_abs ** 4 / 180,
        )
