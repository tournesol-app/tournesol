import numpy as np
from numpy.typing import NDArray

from solidago.primitives.lipschitz import qr_quantile, qr_uncertainty
from solidago.poll import *
from solidago.functions.aggregation.entity_criterion_wise import EntityCriterionWise


class EntitywiseQrQuantile(EntityCriterionWise):
    note: str="entitywise_qr_quantile"
    
    def __init__(self, quantile: float=0.2, lipschitz: float=0.1, error: float=1e-5, *args, **kwargs):
        """ Aggregates scores using the quadratically regularized quantile for each entity and each criterion """
        super().__init__(*args, **kwargs)
        self.quantile = quantile
        self.lipschitz = lipschitz
        self.error = error

    def _args(self,
        variable: tuple[Entity, str], 
        nonargs, # score: MultiScore, with keynames == ["username"]
        voting_rights: VotingRights,
    ) -> tuple[NDArray, NDArray, NDArray, NDArray, float, float, float]:
        return *super()._args(variable, nonargs, voting_rights), self.lipschitz, self.error, self.quantile
        
    def thread_function(self,
        vrights: NDArray, values: NDArray, lefts: NDArray, rights: NDArray,
        lipschitz: float, error: float, quantile: float,
    ) -> tuple[float, float, float]:
        if len(values) == 0:
            return np.nan, np.inf, np.inf
        kwargs = dict(lipschitz=lipschitz, error=error, voting_rights=vrights)
        kwargs |= dict(values=values, left_uncertainties=lefts, right_uncertainties=rights)
        quantile_score = qr_quantile(quantile=quantile, **kwargs)
        median = quantile_score if quantile == 0.5 else None
        uncertainty = qr_uncertainty(default_dev=1.0, median=median, **kwargs)
        return quantile_score, uncertainty, uncertainty

