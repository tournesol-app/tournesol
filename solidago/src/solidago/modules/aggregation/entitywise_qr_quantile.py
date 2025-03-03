import pandas as pd
import numpy as np

from solidago.primitives.lipschitz import qr_quantile, qr_uncertainty
from solidago.state import *
from solidago.modules.base import StateFunction


class EntitywiseQrQuantile(StateFunction):
    def __init__(self, quantile: float=0.2, lipschitz: float=0.1, error: float=1e-5):
        """ Aggregates scores using the quadratically regularized quantile,
        for each entity and each criterion.
        
        Parameters
        ----------
        quantile: float
        lipschitz: float
        error: float
        """
        self.quantile = quantile
        self.lipschitz = lipschitz
        self.error = error
 
    def __call__(self, 
        entities: Entities,
        voting_rights: VotingRights,
        user_models: UserModels,
    ) -> ScoringModel:
        
        global_model = DirectScoring()
        voting_rights = voting_rights.to_dict(["username", "entity_name", "criterion"])
        multiscores = user_models(entities)
        common_kwargs = dict(lipschitz=self.lipschitz, error=self.error)

        for (entity_name, criterion), scores in multiscores.to_dict(["entity_name", "criterion"]):
            rights = np.array([
                voting_rights[username, entity_name, criterion]
                for username, _ in scores
            ], np.float64)
            kwargs = common_kwargs | dict(
                values=np.array(scores["value"], dtype=np.float64),
                voting_rights=rights,
                left_uncertainties=np.array(scores["left_unc"], dtype=np.float64),
                right_uncertainties=np.array(scores["right_unc"], dtype=np.float64),
            )                
            quantile_score = qr_quantile(quantile=self.quantile, **kwargs)
            median = quantile_score if self.quantile == 0.5 else None
            uncertainty = qr_uncertainty(default_dev=1.0, median=median, **kwargs)
            
            global_model.set(entity_name, criterion, quantile_score, uncertainty, uncertainty)
                
        return global_model
