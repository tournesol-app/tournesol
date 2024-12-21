from abc import abstractmethod
from typing import Mapping

import pandas as pd

from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import ScoringModel, ScaledScoringModel
from solidago.voting_rights import VotingRights


class Scaling:
    @abstractmethod
    def __call__(
        self, 
        user_models: Mapping[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame,
        voting_rights: VotingRights,
        privacy: PrivacySettings
    ) -> dict[int, ScaledScoringModel]:
        """ Returns scaled user models
        
        Parameters
        ----------
        user_models: dict[int, ScoringModel]
            user_models[user] is user's scoring model
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        entities: DataFrame with columns
            * entity_id (int, ind)
        voting_rights: VotingRights
            voting_rights[user, entity]: float
        privacy: PrivacySettings
            privacy[user, entity] in { True, False, None }

        Returns
        -------
        out[user]: ScoringModel
            Will be scaled by the Scaling method
        """
        raise NotImplementedError

    def to_json(self) -> tuple:
        return (type(self).__name__, )        

    def __str__(self):
        return type(self).__name__
