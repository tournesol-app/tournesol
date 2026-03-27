""" LipschiTrust does trust propagation with Lipschitz resilience.
    It is described in "Permissionless Collaborative Algorithmic 
    Governance with Security Guarantees", available on ArXiV.
"""

from .base import TrustPropagation

import pandas as pd

from solidago.state_functions.trust_propagation.lipschitrust import LipschiTrust as LipschiTrustSF


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
            The pretrust of a pretrusted user.
            ($Trust^{pre}_{\\checkmark}$ in paper)
            The algorithm guarantees that every pre-trusted user is given a trust score which
            is at least `pretrust_value`. Moreover, all users' trust score will be at most 1.
        decay
            The decay of trusts in voucher's vouchees.
            ($\\beta$ in paper)
            When considering a random walker on the vouch network,
            (1 - `decay`) is the probability that the random walker resets
            its walk at each iteration.
            LipschiTrust essentially robustifies the random walk, by frequently
            preventing the walker from visiting too frequently visited contributors,
            thereby bounding the maximal influence of such contributors.
        sink_vouch
            used to incentivize vouching
            ($V^{sink}_{\\checkmark}$ in paper)
            In our model we assume that each participating contributor implicitly
            vouches for a sink. The sink counts for `sink_vouch` vouchees. As a result, when a
            contributor with less than `sink_vouch` vouchees vouches for more vouchees,
            the amount of trust scores the contributor assigns grows almost
            linearly, thereby not penalizing previously vouched contributors.
            Vouching is thereby not (too) disincentivized.
        error
            Positive, is an upper bound on error, in L1 norm.
            $\\epsilon_{LipschiTrust}$ in paper
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

        state = self.init_state(users, vouches)
        propa = LipschiTrustSF(
            pretrust_value=self.pretrust_value,
            decay=self.decay,
            sink_vouch=self.sink_vouch,
            error=self.error,
        )
        new_state = propa(state)
        return users.assign(
            trust_score=pd.Series(index=new_state.users.keys(), data=new_state.users.values("trust"))
        )

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
