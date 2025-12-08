from numpy.random import random

from solidago.poll import Users, Vouches
from .base import VouchGen


class ErdosRenyiVouch(VouchGen):

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
            usernames_subset = {user.name for user in users if user.is_trustworthy == trustworthy}
            if len(usernames_subset) <= 1: continue
            
            for voucher_name in usernames_subset:
                p_vouch = users[voucher_name].n_expected_vouches / (len(usernames_subset) - 1)
                for vouchee_name in usernames_subset:
                    if (voucher_name != vouchee_name) and (random() < p_vouch):
                        vouches[voucher_name, vouchee_name, "Personhood"] = (1 - random()**2, 0)
        
        return vouches
