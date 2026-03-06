""" LipschiTrust does trust propagation with Lipschitz resilience.
    It is described in "Permissionless Collaborative Algorithmic 
    Governance with Security Guarantees", available on ArXiV.
"""

from copy import deepcopy
from numba import njit

import numpy as np
from numpy.typing import NDArray

from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


class LipschiTrust(PollFunction):
    def __init__(self,
        pretrust_value: float = 0.8,
        decay: float = 0.8,
        sink_vouch: float = 5.0,
        error: float = 1e-8,
        *args, **kwargs,
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

        super().__init__(*args, **kwargs)
        self.pretrust_value = pretrust_value
        self.decay = decay
        self.sink_vouch = sink_vouch
        self.error = error

    def fn(self, users: Users, socials: Socials) -> Users:
        if len(users) == 0:
            return users.assign(trust=list())

        personhood_vouches = socials.filters(kind="Personhood")
        bys = personhood_vouches.get_column("by").map(users.name2index).to_numpy(np.int64)
        tos = personhood_vouches.get_column("to").map(users.name2index).to_numpy(np.int64)
        weights = personhood_vouches.get_column("weight").to_numpy(np.float64)
        pretrusts = users.get_column("pretrust").to_numpy(np.float64) * self.pretrust_value
        
        trusts = type(self).main(bys, tos, weights, pretrusts, self.sink_vouch, self.decay, self.error)
        return users.assign(trust=trusts)
    
    @staticmethod
    # TODO @njit
    def main( 
        bys: NDArray[np.int64],
        tos: NDArray[np.int64],
        weights: NDArray[np.float64],
        pretrusts: NDArray[np.float64],
        sink_vouch: float,
        decay: float,
        error: float,
    ) -> NDArray[np.float64]:
        
        outvouches = np.full_like(weights, sink_vouch)
        for by, weight in zip(bys, weights):
            outvouches[by] += weight

        n_iterations = -np.log(len(weights) / error) / np.log(decay)
        n_iterations = int(np.ceil(n_iterations))
        trusts = deepcopy(pretrusts)
        
        for _ in range(n_iterations):
            # Initialize to pretrust
            new_trusts = pretrusts.copy()
            # Propagate trust through vouches
            for by, to, weight in zip(bys, tos, weights):
                if weight == 0.0:
                    continue
                new_trusts[to] += decay * trusts[by] * weight / outvouches[by]
            # new_trusts[tos] = pretrusts + decay * trusts[bys] * weights / outvouches[bys]

            # Bound trusts for Lipschitz resilience
            new_trusts = new_trusts.clip(max=1.0)
            
            if np.linalg.norm(new_trusts - trusts, ord=1) < error:
                break

            trusts = new_trusts
        
        return trusts
        

    def args_save(self) -> dict[str, float]:
        return dict(
            pretrust_value=self.pretrust_value,
            decay=self.decay,
            sink_vouch=self.sink_vouch,
            error=self.error,
        )
