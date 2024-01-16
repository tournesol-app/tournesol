""" LipschiTrust does trust propagation with Lipschitz resilience.
    It is described in "Permissionless Collaborative Algorithmic 
    Governance with Security Guarantees", available on ArXiV.
"""

from solidago.trust_propagation import TrustPropagation

import pandas as pd
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
        users: pd.DataFrame,
        vouches: pd.DataFrame
    ) -> pd.DataFrame:
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
        - users: DataFrame with columns
            * user_id (int, index)
            * is_pretrusted (bool)
            * trust_score (float)
        """
        total_vouches = dict(vouches["voucher"].value_counts())
        for voucher in total_vouches:
            total_vouches[voucher] += self.sink_vouch
            
        pretrusts = np.array(users["is_pretrusted"] * self.pretrust_value)
        trusts = np.array(pretrusts)

        n_iterations = - np.log(len(users)/self.error) / np.log(self.decay)
        n_iterations = int(np.ceil( n_iterations ))
        for _ in range(n_iterations):
            # Initialize to pretrust
            new_trusts = np.array(pretrusts)
            # Propagate trust through vouches
            for _, row in vouches.iterrows():
                vouch = row["vouch"] / total_vouches[row["voucher"]]
                new_trusts[row["vouchee"]] += self.decay * trusts[row["voucher"]] * vouch
            # Bound trusts for Lipschitz resilience
            trusts = new_trusts.clip(max=1.0)
        
        return users.assign(trust_score=trusts)
      
    def __str__(self):
        prop_names = ["pretrust_value", "decay", "sink_vouch", "error"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"LipschiTrust({prop})"
