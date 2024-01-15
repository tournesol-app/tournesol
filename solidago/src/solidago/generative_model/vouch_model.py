from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

class VouchModel(ABC):
    @abstractmethod
    def __call__(self, users: pd.DataFrame):
        """ Generates vouches between users
        Inputs:
        - users: DataFrame with columns
            * `user_id`: int
            * And maybe more
        
        Returns:
        - vouches: DataFrame with columns
            * `voucher`: int
            * `vouchee`: int
            * `vouch`: float
        """
        raise NotImplementedError

class ErdosRenyiVouchModel(VouchModel):
    def __call__(self, users: pd.DataFrame):
        """ Generates vouches between users
        Inputs:
        - users: DataFrame with columns
            * `user_id`: int
            * `is_trustworthy`: bool
            * `n_expected_vouches`: float
        
        Returns:
        - vouches: DataFrame with columns
            * `voucher`: int
            * `vouchee`: int
            * `vouch`: float
        """
        vouchers, vouchees, vouches = list(), list(), list()
        n_trustworthy = len(users[users["is_trustworthy"]])
        
        for voucher, voucher_row in users.iterrows():
            # Determine the probability to vouch, depending on trustworthiness
            if voucher_row["is_trustworthy"] and n_trustworthy == 0:
                p_vouch = voucher_row["n_expected_vouches"] / n_trustworthy
            else:
                p_vouch = voucher_row["n_expected_vouches"] / (len(users) - n_trustworthy)
            
            for vouchee, vouchee_row in users.iterrows():
                if voucher == vouchee:
                    continue
                can_vouch = (voucher_row["is_trustworthy"] == vouchee_row["is_trustworthy"])
                if can_vouch and (np.random.random() < p_vouch):
                    vouchers.append(voucher)
                    vouchees.append(vouchee)
                    vouches.append(1)
                    
        return pd.DataFrame(dict(voucher=vouchers, vouchee=vouchees, vouch=vouches))
