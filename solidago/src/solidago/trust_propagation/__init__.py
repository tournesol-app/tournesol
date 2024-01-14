""" Trust propagation is tasked to combine pretrusts and vouches
    to derive trust scores for the different users
"""

from pandas import DataFrame
from abc import abstractmethod

class TrustPropagation:
    def __init__(self):
		    pass
		    
    @abstractmethod
    def compute_trusts(self,
        users: DataFrame,
        vouches: DataFrame
    ) -> dict[str, float]:
        """
		    Inputs:
		    - users: DataFrame with columns
            * public_username (str, index)
            * is_pretrusted (bool)
		    - vouches: DataFrame with columns
            * voucher (str)
            * vouchee (str)
            * vouch (float)
		    
		    Returns:
				- trusts: dict, where trusts[user] (float) is the trust in user
		    """
        pass
		
