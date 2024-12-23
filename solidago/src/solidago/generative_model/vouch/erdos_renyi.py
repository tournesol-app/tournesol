from solidago.state import Users, Vouches
from .base import VouchGenerator

import numpy as np


class ErdosRenyiVouchGenerator(VouchGenerator):
    
    def __call__(self, users: Users) -> Vouches:
        """ Each vouch is sampled independently, with a probability dependent on users' metadata.
        Each user must have the two keys `is_trustworthy: bool` and `n_expected_vouches: float`.
        Trustworthy vouchers only vouch for trustworthy vouchees,
        and untrustworthy vouchers only vouch for untrustworthy vouchees.
        The probability of a vouch from `voucher` to `vouchee` is given by
        `voucher["n_expected_vouches"] / len({ user if user["is_trustworthy"] == voucher["is_trustworthy"] })`,
        assuming the voucher and vouchee have the same "is_trustworthy" value.
        """
        vouches = Vouches()
        
        for trustworthy in (True, False):
            users_subset = Users(users[users["is_trustworthy"] == trustworthy])
            if len(users_subset) <= 1: continue
            
            for voucher in users_subset:
                p_vouch = voucher["n_expected_vouches"] / (len(users_subset) - 1)
                for vouchee in users_subset:
                    if (voucher.name != vouchee.name) and (np.random.random() < p_vouch):
                        vouches[voucher, vouchee] = 1 - np.random.random()**2
        
        return vouches
