""" LipschiTrust does trust propagation with Lipschitz resilience.
    It is described in "Permissionless Collaborative Algorithmic 
    Governance with Security Guarantees", available on ArXiV.
"""

from solidago.trust_propagation import TrustPropagation
from pandas import DataFrame
import numpy as np

class LipschiTrust(TrustPropagation):
    def __init__(self,
        pretrust_value: float=0.8,
        decay: float=0.8,
        sink_vouch: float=5.0,
        error: float=1e-8
    ):
        """ A robustified variant of PageRank
        Inputs:
        - pretrust_value is the pretrust of a pretrusted user
            (Trust^{pre}_{checkmark} in paper)
        - decay is the decay of trusts in voucher's vouchees
            (beta in paper)
        - sink_vouch is the vouch to none, used to incentivize vouching
            (V^{sink}_{checkmark} in paper)
        - error > 0 is an upper bound on error (in L1 norm)
            (epsilon_{LipschiTrust} in paper)
        """
        assert pretrust_value >= 0 and pretrust_value <= 1
        assert decay >= 0 and decay <= 1
        assert sink_vouch >= 0
        assert error > 0
        
        self.pretrust_value = pretrust_value
        self.decay = decay
        self.sink_vouch = sink_vouch
        self.error = error
    
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
        rsv = self.received_scaled_vouches(vouches)
        pretrusts = set(users.loc[users["is_pretrusted"]].index)
        trusts = { u: self.pretrust_value for u in pretrusts }

        n_iterations = - np.log(len(users)/self.error) / np.log(self.decay)
        n_iterations = int(np.ceil( n_iterations ))
        for _ in range(n_iterations):
            # Initialize to pretrust
            new_trusts = dict()
            for user in pretrusts:
                new_trusts[user] = self.pretrust_value
            # Propagate trust through vouches
            for vouchee in rsv:
                if vouchee not in new_trusts:
                    new_trusts[vouchee] = 0
                for voucher in rsv[vouchee]:
                    if voucher not in trusts: continue
                    flow = trusts[voucher] * rsv[vouchee][voucher]
                    new_trusts[vouchee] += self.decay * flow
            # Bound trusts for Lipschitz resilience
            for user in new_trusts:
                trusts[user] = min(new_trusts[user], 1.0)

        return trusts
      
    def received_scaled_vouches(self,
        vouches: DataFrame
    ) -> dict[str, dict[str, float]]:
        """
        Inputs:
        - vouches is a list of tuples (voucher, vouchee, scaled_vouch)
        
        Returns:
        - v[vouchee][voucher] is the scaled vouch recevied by vouchee
            from voucher
        """
        total_vouches = dict(vouches["voucher"].value_counts())
        for voucher in total_vouches:
            total_vouches[voucher] += self.sink_vouch
        
        rsv = dict()
        for _, row in vouches.iterrows():
            voucher, vouchee = row["voucher"], row["vouchee"]
            scaled_vouch = row["vouch"] / total_vouches[voucher]
            if vouchee not in rsv: rsv[vouchee] = dict()
            rsv[vouchee][voucher] = scaled_vouch
        return rsv
    
