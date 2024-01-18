from abc import ABC, abstractmethod

import pandas as pd

from .compute_voting_rights import compute_voting_rights

class VotingRights(ABC):
    @abstractmethod
    def __call__(
        self,
        users: pd.DataFrame,
        vouches: pd.DataFrame,
        privacy: pd.DataFrame,
        comparisons: pd.DataFrame
    ) -> dict[int, dict[int, dict[str, float]]]:
        """ Compute voting rights
        
        Parameters
        ----------
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        vouches: DataFrame with columns
            * voucher (int)
            * vouchee (int)
            * vouch (float)
        comparisons: DataFrame with columns
            * user_id (int)
            * criteria (int)
            * entity_a (int)
            * entity_b (int)
            * score (float)
        
        Returns
        -------
        voting_rights[user][entity][criterion] is the voting right
            of a user on entity for criterion
        """
        raise NotImplementedError
    
