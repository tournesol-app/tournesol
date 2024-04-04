import pandas as pd
import numpy as np

from .base import Scaling

from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import ScoringModel, ScaledScoringModel
from solidago.voting_rights import VotingRights
from solidago.primitives import qr_standard_deviation


class Standardize(Scaling):
    def __init__(self, dev_quantile: float=0.9, lipschitz: float=0.1, error: float=1e-5):
        """ The scores are shifted so that their quantile zero_quantile equals zero
        
        Parameters
        ----------
        zero_quantile: float
        """
        self.dev_quantile = dev_quantile
        self.lipschitz = lipschitz
        self.error = error
    
    def __call__(
        self, 
        user_models: dict[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame,
        voting_rights: VotingRights,
        privacy: PrivacySettings
    ):
        df = _get_user_scores(voting_rights, user_models, entities)
        std_dev = self._compute_std_dev(df)
        return {
            user: ScaledScoringModel(user_models[user], 1/std_dev)
            for user in user_models
        }
    
    def _compute_std_dev(self, df):
        return qr_standard_deviation(
            lipschitz=self.lipschitz, 
            values=np.array(df["scores"]), 
            quantile_dev=self.dev_quantile,
            voting_rights=np.array(df["voting_rights"]), 
            left_uncertainties=np.array(df["left_uncertainties"]), 
            right_uncertainties=np.array(df["right_uncertainties"]), 
            default_dev=1, 
            error=self.error
        )
    
    def to_json(self):
        return type(self).__name__, dict(dev_quantile=self.dev_quantile, 
            lipschitz=self.lipschitz, error=self.error)

    def __str__(self):
        prop_names = ["dev_quantile", "lipschitz", "error"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"

def _get_user_scores(
    voting_rights: VotingRights,
    user_models: dict[int, ScoringModel],
    entities: pd.DataFrame
):
    user_list, entity_list, voting_right_list = list(), list(), list()
    scores, lefts, rights = list(), list(), list()
    for user_id, scoring_model in user_models.items():
        for entity in scoring_model.scored_entities(entities):
            user_list.append(user_id)
            entity_list.append(entity)
            voting_right_list.append(voting_rights[user_id, entity])
            output = scoring_model(entity, entities.loc[entity])
            scores.append(output[0])
            lefts.append(output[1])
            rights.append(output[2])
                
    return pd.DataFrame(dict(
        user_id=user_list,
        entity_id=entity_list,
        voting_rights=voting_right_list,
        scores=scores,
        left_uncertainties=lefts,
        right_uncertainties=rights,
    ))
    
