""" Trust propagation is tasked to combine pretrusts and vouches
    to derive trust scores for the different users
"""

from pandas import DataFrame
from abc import ABC, abstractmethod

class TrustPropagation(ABC):
    @abstractmethod
    def __call__(self,
        users: DataFrame,
        vouches: DataFrame
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
				- trusts: dict, where trusts[user] (float) is the trust in user
		    """
        pass
		
