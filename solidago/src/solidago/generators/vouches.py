import numpy as np

from solidago.poll import User, Users, Vouches
from solidago.poll_functions.poll_function import PollFunction


class ErdosRenyi(PollFunction):
    def fn(self, users: Users) -> Vouches:
        """ Each vouch is sampled independently, with a probability dependent on users' metadata.
        Each user must have the two keys `trustworthy: bool` and `n_expected_vouches: float`.
        Trustworthy vouchers only vouch for trustworthy vouchees,
        and untrustworthy vouchers only vouch for untrustworthy vouchees.
        The probability of a vouch from `voucher` to `vouchee` is given by
        `voucher["expected_n_vouches"] / len({ user if user["trustworthy"] == voucher["trustworthy"] })`,
        assuming the voucher and vouchee have the same "trustworthy" value.
        """
        vouches = Vouches()
        for user in users:
            assert "trustworthy" in user
            assert "expected_n_vouches" in user
        
        for trustworthy in (True, False):
            usernames_subset = {user.name for user in users if user["trustworthy"] == trustworthy}
            if len(usernames_subset) <= 1: continue
            
            for by in usernames_subset:
                user = users[by]
                assert isinstance(user, User)
                p_vouch = user["expected_n_vouches"] / (len(usernames_subset) - 1)
                for to in usernames_subset:
                    if (by != to) and (np.random.random() < p_vouch):
                        value = (1 - np.random.random()**2, 0)
                        vouches.set(by=by, to=to, kind="Personhood", value=value)
        
        return vouches
        
