import pandas as pd
import numpy as np

from .voting_rights import VotingRights
from .base import VotingRightsAssignment


class IsTrust(VotingRightsAssignment):
    def __init__(self, privacy_penalty: float=0.5):
        self.privacy_penalty = privacy_penalty
    
    def __call__(
        self,
        users: pd.DataFrame,
        entities: pd.DataFrame,
        vouches: pd.DataFrame,
        privacy: pd.DataFrame
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
        
        Returns
        -------
        voting_rights[user, entity] is the voting right
            of a user on entity for criterion
        entities: DataFrame with columns
            * entity_id (int, index)
        """
        voting_rights = VotingRights()
        
        for user in users.index:
            for entity in entities.index:
                if privacy[user, entity] is None:
                    continue
                voting_rights[user, entity] = privacy[user, entity] * self.privacy_penalty
                voting_rights[user, entity] *= users.loc[user, "trust_score"]
                
        return voting_rights
    
    def to_json(self):
        return (type(self).__name__, )
    
