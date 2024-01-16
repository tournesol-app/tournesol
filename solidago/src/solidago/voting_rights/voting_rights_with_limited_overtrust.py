import pandas as pd
import numpy as np

from . import VotingRights

class VotingRightsWithLimitedOvertrust(VotingRights):
    def __init__(
        self, 
        privacy_penalty: float = 0.5, 
        min_overtrust: float = 2.0,
        overtrust_ratio: float = 0.1,
    ):
        """ privately scored entities are given 
        """
        self.privacy_penalty = privacy_penalty
        self.min_overtrust = min_overtrust
        self.overtrust_ratio = overtrust_ratio
    
    def __call__(
        users: pd.DataFrame,
        vouches: pd.DataFrame,
        comparisons: pd.DataFrame
    ) -> dict[int, dict[int, dict[str, float]]]:
        """ Compute voting rights
        Inputs:
        - users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        - vouches: DataFrame with columns
            * voucher (int)
            * vouchee (int)
            * vouch (float)
        - comparisons: DataFrame with columns
            * user_id (int)
            * criteria (int)
            * entity_a (int)
            * entity_b (int)
            * score (float)
        
        Returns:
        - voting_rights[user][entity][criterion] is the voting right
            of a user on entity for criterion
        """
        raise NotImplementedError
    
