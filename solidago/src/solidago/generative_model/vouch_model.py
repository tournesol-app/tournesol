from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

class VouchModel(ABC):
    @abstractmethod
    def __call__(self, users: pd.DataFrame):
        """ Generates vouches between users
        
        Parameters
        ----------
        users: DataFrame with columns
            * `user_id`: int
            * And maybe more
        
        Returns
        -------
        vouches: DataFrame with columns
            * `voucher`: int
            * `vouchee`: int
            * `vouch`: float
        """
        raise NotImplementedError
    
    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )


class ErdosRenyiVouchModel(VouchModel):
    def __call__(self, users: pd.DataFrame):
        """ Generates vouches between users
        
        Parameters
        ----------
        users: DataFrame with columns
            * `user_id`: int
            * `is_trustworthy`: bool
            * `n_expected_vouches`: float
        
        Returns
        -------
        vouches: DataFrame with columns
            * `voucher`: int
            * `vouchee`: int
            * `vouch`: float
        """
        vouch_list = list()
        n_trustworthy = len(users[users["is_trustworthy"]])
        
        for voucher, voucher_row in users.iterrows():
            # Determine the probability to vouch, depending on trustworthiness
            if voucher_row["is_trustworthy"]:
                p_vouch = voucher_row["n_expected_vouches"] / n_trustworthy
            else:
                p_vouch = voucher_row["n_expected_vouches"] / (len(users) - n_trustworthy)
            
            for vouchee, vouchee_row in users.iterrows():
                if voucher == vouchee:
                    continue
                can_vouch = (voucher_row["is_trustworthy"] == vouchee_row["is_trustworthy"])
                if can_vouch and (np.random.random() < p_vouch):
                    vouch_list.append((voucher, vouchee, 1 - np.random.random()**2))
        
        if len(vouch_list) == 0:
            return pd.DataFrame(columns=["voucher", "vouchee", "vouch"])
        
        v = list(zip(*vouch_list))
        return pd.DataFrame(dict(voucher=v[0], vouchee=v[1], vouch=v[2]))

