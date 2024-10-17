""" LipschiTrust does trust propagation with Lipschitz resilience.
    It is described in "Permissionless Collaborative Algorithmic 
    Governance with Security Guarantees", available on ArXiV.
"""

from .base import TrustPropagation

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

        Parameters
        ----------
        pretrust_value:
            the pretrust of a pretrusted user.  
            (`Trust^{pre}_{checkmark}` in paper)
        decay:
            the decay of trusts in voucher's vouchees.  
            (`beta` in paper)
        sink_vouch: is the vouch to none, used to incentivize vouching
            (V^{sink}_{checkmark} in paper)
        error: > 0 is an upper bound on error (in L1 norm)
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
        if len(users) == 0:
            return users.assign(trust_score=[])

        total_vouches = vouches["voucher"].value_counts() + self.sink_vouch            
        pretrusts = users["is_pretrusted"] * self.pretrust_value
        trusts = pretrusts.copy()

        n_iterations = - np.log(len(users)/self.error) / np.log(self.decay)
        n_iterations = int(np.ceil( n_iterations ))
        for _ in range(n_iterations):
            # Initialize to pretrust
            new_trusts = pretrusts.copy()
            # Propagate trust through vouches
            for row in vouches.itertuples():
                discount = self.decay * row.vouch / total_vouches[row.voucher]
                new_trusts[row.vouchee] += discount * trusts[row.voucher]

            # Bound trusts for Lipschitz resilience
            new_trusts = new_trusts.clip(upper=1.0)

            delta = np.linalg.norm(new_trusts - trusts, ord=1)
            trusts = new_trusts
            if delta < self.error:
                break
        
        return users.assign(trust_score=trusts)
      
    def __str__(self):
        prop_names = ["pretrust_value", "decay", "sink_vouch", "error"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"LipschiTrust({prop})"

    def to_json(self):
        return "LipschiTrust", dict(
            pretrust_value=self.pretrust_value,
            decay=self.decay,
            sink_vouch=self.sink_vouch,
            error=self.error
        )
