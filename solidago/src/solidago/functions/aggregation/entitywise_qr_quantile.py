import pandas as pd
import numpy as np

from solidago.primitives.lipschitz import qr_quantile, qr_uncertainty
from solidago.poll import *
from solidago.functions.aggregation.entity_criterion_wise import EntityCriterionWise


class EntitywiseQrQuantile(EntityCriterionWise):
    note: str="entitywise_qr_quantile"
    
    def __init__(self, quantile: float=0.2, lipschitz: float=0.1, error: float=1e-5, *args, **kwargs):
        """ Aggregates scores using the quadratically regularized quantile,
        for each entity and each criterion.
        
        Parameters
        ----------
        quantile: float
        lipschitz: float
        error: float
        """
        super().__init__(*args, **kwargs)
        self.quantile = quantile
        self.lipschitz = lipschitz
        self.error = error

    def aggregate(self, scores: MultiScore, voting_rights: VotingRights) -> Score:
        if len(scores) == 0:
            return Score.nan()
        kwargs = dict(lipschitz=self.lipschitz, error=self.error) | dict(
            values=np.array([ s.value for _, s in scores ], dtype=np.float64),
            voting_rights=np.array([ voting_rights[u] for (u,), _ in scores ], np.float64),
            left_uncertainties=np.array([ s.left_unc for _, s in scores ], dtype=np.float64),
            right_uncertainties=np.array([ s.right_unc for _, s in scores ], dtype=np.float64),
        )                
        quantile_score = qr_quantile(quantile=self.quantile, **kwargs)
        median = quantile_score if self.quantile == 0.5 else None
        uncertainty = qr_uncertainty(default_dev=1.0, median=median, **kwargs)
        return Score(quantile_score, uncertainty, uncertainty)
