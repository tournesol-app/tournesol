""" TrustAll is a naive solution that assignes an equal amount of trust to all users
"""

from .base import TrustPropagation

import pandas as pd
import numpy as np

class TrustAll(TrustPropagation):
    def __call__(self,
        users: pd.DataFrame,
        vouches: pd.DataFrame
    ) -> dict[str, float]:
        """
        Inputs:
        - users: DataFrame with columns
            * user_id (int, index)
            * is_pretrusted (bool)
        - vouches: DataFrame with columns
            * voucher (str)
            * vouchee (str)
            * vouch (float)
        
        Returns:
        - users: DataFrame with columns
            * user_id (int, index)
            * is_pretrusted (bool)
            * trust_score (float)
        """
        return users.assign(trust_score=[1.0] * len(users))
    
      
