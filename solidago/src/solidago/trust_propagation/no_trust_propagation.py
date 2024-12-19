import pandas as pd

from .base import TrustPropagation


class NoTrustPropagation(TrustPropagation):
    def __init__(self, pretrust_value: float=0.8,):
        """
        Implements no trust propagation.
        The result trust_score is directly based on the "pretrusted" status of each user.

        Parameters
        ----------
        pretrust_value:
            trust score to assign to pretrusted users
        """
        self.pretrust_value = pretrust_value

    def __call__(self,
        users: pd.DataFrame,
        vouches: pd.DataFrame
    ) -> pd.DataFrame:
        return users.assign(trust_score=users["is_pretrusted"] * self.pretrust_value)
        
    def __str__(self):
        return f"{type(self).__name__}(pretrust_value={self.pretrust_value})"
		
    def to_json(self):
        return (type(self).__name__, { "pretrust_value": self.pretrust_value })
