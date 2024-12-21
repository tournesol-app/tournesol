""" LipschiTrust does trust propagation with Lipschitz resilience.
    It is described in "Permissionless Collaborative Algorithmic 
    Governance with Security Guarantees", available on ArXiV.
"""

from .base import TrustPropagation

import pandas as pd
import numpy as np


class LipschiTrust(TrustPropagation):
    def __init__(
        self,
        pretrust_value: float = 0.8,
        decay: float = 0.8,
        sink_vouch: float = 5.0,
        error: float = 1e-8,
    ):
        """A robustified variant of PageRank.
        In this algorithm, we leverage pre-trust (e.g., based on email domains) and
        vouching to securely assign trust scores to a wider set of contributors. The
        algorithm inputs pre-trust status and a vouching directed graph.

        Parameters
        ----------
        pretrust_value
            the pretrust of a pretrusted user.
            (`Trust^{pre}_{checkmark}` in paper)
            The algorithm guarantees that every pre-trusted user is given a trust score which
            is at least `pretrust_value`. Moreover, all users' trust score will be at most 1.
        decay
            the decay of trusts in voucher's vouchees.
            (`beta` in paper)
            When considering a random walker on the vouch network,
            (1 - `decay`) is the probability that the random walker resets
            its walk at each iteration.
            LipschiTrust essentially robustifies the random walk, by frequently
            preventing the walker from visiting too frequently visited contributors,
            thereby bounding the maximal influence of such contributors.
        sink_vouch
            used to incentivize vouching
            (V^{sink}_{checkmark} in paper)
            In our model we assume that each participating contributor implicitly
            vouches for a sink. The sink counts for `sink_vouch` vouchees. As a result, when a
            contributor with less than `sink_vouch` vouchees vouches for more vouchees,
            the amount of trust scores the contributor assigns grows almost
            linearly, thereby not penalizing previously vouched contributors.
            Vouching is thereby not (too) disincentivized.
        error
            >0, is an upper bound on error (in L1 norm)
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

    def __call__(self, users: pd.DataFrame, vouches: pd.DataFrame) -> pd.DataFrame:
        if len(users) == 0:
            return users.assign(trust_score=[])

        total_vouches = vouches["voucher"].value_counts() + self.sink_vouch
        pretrusts = users["is_pretrusted"] * self.pretrust_value
        trusts = pretrusts.copy()

        n_iterations = -np.log(len(users) / self.error) / np.log(self.decay)
        n_iterations = int(np.ceil(n_iterations))
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
            error=self.error,
        )
