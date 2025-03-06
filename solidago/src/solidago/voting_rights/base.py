from abc import ABC, abstractmethod

import pandas as pd

from solidago.scoring_model import ScoringModel
from solidago.privacy_settings import PrivacySettings
from .voting_rights import VotingRights


class VotingRightsAssignment(ABC):
    @abstractmethod
    def __call__(
        self,
        users: pd.DataFrame,
        entities: pd.DataFrame,
        vouches: pd.DataFrame,
        privacy: PrivacySettings,
        user_models: dict[int, "ScoringModel"]
    ) -> tuple[VotingRights, pd.DataFrame]:
        """ Compute voting rights
        
        Parameters
        ----------
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        entities: DataFrame with columns
            * entity_id (int, index)
        vouches: DataFrame with columns
            * voucher (int)
            * vouchee (int)
            * vouch (float)
        privacy: PrivacySettings
            privacy[user, entity] in { True, False, None }
        user_models: dict[int, ScoringModel]
            user_models[user_id] is the user's scoring model
        
        Returns
        -------
        voting_rights[user, entity] is the voting right
            of a user on entity for criterion
        entities: DataFrame with columns
            * entity_id (int, index)
        """
        raise NotImplementedError
    
    def to_json(self):
        return (type(self).__name__, )
    
    def __str__(self):
        return type(self).__name__
