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

from solidago.state import *
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
        last_comparison_only: bool=True,
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
        last_comparison_only: bool=True
            Ignores all comparisons between two entities prior to the last provided.
        """
        super().__init__(
            prior_std_dev=prior_std_dev,
            uncertainty_nll_increase=uncertainty_nll_increase,
            max_uncertainty=max_uncertainty,
            last_comparison_only=last_comparison_only,
        )
        self.convergence_error = convergence_error
        self.max_iter = max_iter
        self.device = device

    @abstractmethod
    def torch_cumulant_generating_function(self, score_diffs: torch.Tensor) -> torch.Tensor:
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

    def init_values(self, entities: Entities, init: MultiScore) -> torch.Tensor:
        """ To avoid nan errors in autograd, we initialize at nonzero values """
        values = 1e-3 * torch.normal(0, 1, (len(entities),))
        for index, entity in enumerate(entities):
            if not np.isnan(init[entity].value):
                values[index] = init[entity].value * (1 + values[index])
        values.requires_grad = True
        values = values.to(self.device)
        return values
    
    def compute_values(self, 
        entities: Entities,
        comparisons: Comparisons, # keynames == ["entity_name", "other_name"]
        init : MultiScore, # keynames == "entity_name"
    ) -> npt.NDArray:
        """ Computes the scores given comparisons """
        values = self.init_values(entities, init)
        left_indices, right_indices = comparisons.left_right_indices(entities)
        normalized_comparisons = torch.tensor(comparisons.normalized_comparison_list())
        negative_log_posterior_args = left_indices, right_indices, normalized_comparisons
            
        lbfgs = torch.optim.LBFGS(
            (values,),
            max_iter=self.max_iter,
            tolerance_change=self.convergence_error,
            line_search_fn="strong_wolfe",
        )
        
        def closure():
            lbfgs.zero_grad()
            loss = self.negative_log_posterior(values, *negative_log_posterior_args)
            loss.backward()
            return loss

        lbfgs.step(closure)  # type: ignore

        n_iter = lbfgs.state_dict()["state"][0]["n_iter"]
        if n_iter >= self.max_iter:
            raise RuntimeError(f"LBFGS failed to converge in {n_iter} iterations")

        values = values.detach()
        if values.isnan().any():
            raise RuntimeError(f"Nan in solution, state: {lbfgs.state_dict()}")
        return np.array(values)
            
    def negative_log_posterior(self, 
        values: torch.Tensor,
        left_indices: list[int],
        right_indices: list[int],
        normalized_comparisons: torch.Tensor,
    ) -> torch.Tensor:
        """ Negative log posterior """
        value_diffs = values[left_indices] - values[right_indices]
        loss = self.torch_cumulant_generating_function(value_diffs).sum()
        loss += (value_diffs * normalized_comparisons).sum()
        return loss + (values**2).sum() / (2 * self.prior_std_dev**2)


class LBFGSUniformGBT(LBFGSGeneralizedBradleyTerry, UniformGBT):
    def __init__(self,
        prior_std_dev: float=7,
        uncertainty_nll_increase: float=1.0,
        max_uncertainty: float=1e3,
        convergence_error: float=1e-5,
        max_iter: int=100,
        device: torch.device=default_device,
        last_comparison_only: bool=True,
        cgf_epsilon: float=1e-8,
    ):
        """ Generalized Bradley Terry with a uniform root law is a straightforward
        instance of the models introduced in the paper "Generalized Bradley-Terry 
        Models for Score Estimation from Paired Comparisons" by Julien Fageot, 
        Sadegh Farhadkhani, Lê-Nguyên Hoang and Oscar Villemaud, and published at AAAI'24.
        
        This implementation leverages Limited-memory Broyden-Fletcher-Goldfarb-Shanno 
        (LBFGS) algorithm, a second-order quasi-Newton method with limited demands 
        of computer memory. In particular we use its pytorch implementation.
        
        Parameters
        ----------
        prior_std_dev: float=7.0
            Typical scale of values. 
            Technical, it should be the standard deviation of the gaussian prior.
        convergence_error: float=1e-5
            Admissible error in value computations (obtained through optimization).
        high_likelihood_range_threshold: float=1.0
            To determine the uncertainty, we compute left_unc (respectively, right_unc)
            such that value - left_unc (respectively, + right_unc) has a likelihood
            which is exp(high_likelihood_range_threshold) times lower than value.
        max_uncertainty: float=1e3
            Replaces infinite uncertainties with max_uncertainty
        last_comparison_only: bool=True
            Ignores all comparisons between two entities prior to the last provided.
        """
        super().__init__(
            prior_std_dev=prior_std_dev,
            uncertainty_nll_increase=uncertainty_nll_increase,
            max_uncertainty=max_uncertainty,
            convergence_error=convergence_error,
            max_iter=max_iter,
            device=device,
            last_comparison_only=last_comparison_only
        )
        self.cgf_epsilon = cgf_epsilon

    def torch_cumulant_generating_function(self, value_diffs: torch.Tensor) -> torch.Tensor:
        """ Vectorized cumulant generating function adapted for pytorch

        Parameters
        ----------
        value_diffs: torch.Tensor
            Score difference

        Returns
        -------
        cgf: torch.Tensor
            cfg[i] is the cgf of value_diff[i]
        """
        value_diffs_abs = (value_diffs**2 + self.cgf_epsilon).sqrt()
        return torch.where(
            value_diffs_abs > 1e-1,
            torch.where(
                value_diffs_abs < 20.0,
                (torch.sinh(value_diffs_abs.clip(max=20.)) / (self.cgf_epsilon + value_diffs_abs)).log(),
                value_diffs_abs - np.log(2) - value_diffs_abs.log(),
            ),
            value_diffs_abs ** 2 / 6 - value_diffs_abs ** 4 / 180,
        )
