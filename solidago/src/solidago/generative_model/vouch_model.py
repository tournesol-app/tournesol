from abc import ABC, abstractmethod

import pandas as pd

class VouchModel(ABC):
    @abstractmethod
    def __call__(self, users: pd.DataFrame, entities: pd.DataFrame):
        """ Generates vouches between users
        Inputs:
        - users: DataFrame with columns
            * `user_id`: int
            * `is_pretrusted`: bool
            * And maybe more
        
        Returns:
        - vouches: DataFrame with columns
            * `voucher`: int
            * `vouchee`: int
            * `vouch`: float
        """
        raise NotImplementedError

