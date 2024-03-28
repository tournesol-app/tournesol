import pandas as pd

from .base import TrustPropagation


class NoTrustPropagation(TrustPropagation):
    def __init__(self, pretrust_value: float=0.8,):
        self.pretrust_value = pretrust_value

    def __call__(self,
        users: pd.DataFrame,
        vouches: pd.DataFrame
    ) -> pd.DataFrame:
        """ Propagates trust through vouch network
        
        Parameters
        ----------
        users: DataFrame with columns
            * user_id (int, index)
            * is_pretrusted (bool)
        vouches: DataFrame with columns
            * voucher (str)
            * vouchee (str)
            * vouch (float)
        
        Returns
        -------
        users: DataFrame with columns
            * user_id (int, index)
            * is_pretrusted (bool)
            * trust_score (float)
        """
        return users.assign(trust_score=users["is_pretrusted"] * pretrust_value)
        
    def __str__(self):
        return f"{type(self).__name__}(pretrust_value={self.pretrust_value})"
		
    def to_json(self):
        return (type(self).__name__, { "pretrust_value": self.pretrust_value })
