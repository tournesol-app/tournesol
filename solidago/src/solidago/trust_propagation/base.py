from abc import ABC, abstractmethod

import pandas as pd

class TrustPropagation(ABC):
    """
    Base class for Trust Propagation algorithms
    """

    @abstractmethod
    def __call__(self,
        users: pd.DataFrame,
        vouches: pd.DataFrame
    ) -> pd.DataFrame:
        """ Propagates trust through vouch network
        
        Parameters
        ----------
        users: DataFrame
            with columns

            * user_id (int, index)
            * is_pretrusted (bool)

        vouches: DataFrame
            with columns

            * voucher (str)
            * vouchee (str)
            * vouch (float)
        
        Returns
        -------
        users: DataFrame
            with columns

            * user_id (int, index)
            * is_pretrusted (bool)
            * trust_score (float)
        """
        raise NotImplementedError
        
    def __str__(self):
        return type(self).__name__
		
    def to_json(self):
        return (type(self).__name__, )
