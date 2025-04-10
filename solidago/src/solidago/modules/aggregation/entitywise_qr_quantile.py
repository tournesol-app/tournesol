import pandas as pd
import numpy as np

from solidago.primitives.lipschitz import qr_quantile, qr_uncertainty
from solidago.state import *
from solidago.modules.base import StateFunction


class EntitywiseQrQuantile(StateFunction):
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
 
    def __call__(self, 
        entities: Entities,
        voting_rights: VotingRights,
        user_models: UserModels,
    ) -> ScoringModel:
        
        global_model = DirectScoring(note="entitywise_qr_quantile")
        multiscores = user_models(entities)
        common_kwargs = dict(lipschitz=self.lipschitz, error=self.error)

        for (entity_name, criterion), scores in multiscores.iter("entity_name", "criterion"):
            v = voting_rights.get(entity_name=entity_name, criterion=criterion)
            kwargs = common_kwargs | dict(
                values=np.array([ s.value for _, s in scores ], dtype=np.float64),
                voting_rights=np.array([ v[username] for username, _ in scores ], np.float64),
                left_uncertainties=np.array([ s.left_unc for _, s in scores ], dtype=np.float64),
                right_uncertainties=np.array([ s.right_unc for _, s in scores ], dtype=np.float64),
            )                
            quantile_score = qr_quantile(quantile=self.quantile, **kwargs)
            median = quantile_score if self.quantile == 0.5 else None
            uncertainty = qr_uncertainty(default_dev=1.0, median=median, **kwargs)
            global_model[entity_name, criterion] = Score(quantile_score, uncertainty, uncertainty)
                
        return global_model
