import numpy as np

from solidago.poll import *
from solidago.primitives.random import Distribution, Uniform
from solidago.functions.poll_function import PollFunction


class ErdosRenyiVouch(PollFunction):
    default_timestamp = Uniform(0, 1000)

    def __init__(self, 
        default_trustworthy: bool = True, 
        default_expected_n_vouches: float = 5.,
        timestamp: Distribution | tuple[str, dict] | None = None,
    ):
        self.default_trustworthy = default_trustworthy
        self.default_expected_n_vouches = default_expected_n_vouches
        import solidago, solidago.primitives.random as r
        self.timestamp = solidago.load(timestamp, r, Distribution, self.default_timestamp)

    def fn(self, users: Users, socials: Socials) -> Socials:
        if "trustworthy" not in users.columns:
            users = users.assign(trustworthy=self.default_trustworthy)
        for trustworthy in (True, False):
            subusers = users.filters(trustworthy=trustworthy)
            if len(subusers) <= 1: continue
            
            for by in subusers:
                expected_n_vouches = by.get("expected_n_vouches", self.default_expected_n_vouches)
                p_vouch = expected_n_vouches / (len(subusers) - 1)
                for to in subusers:
                    if (by != to) and (np.random.random() < p_vouch):
                        socials.set(
                            by=by.name, to=to.name, kind="Personhood", 
                            weight=1-np.random.random()**2,
                            timestamp=self.timestamp.sample()[0]
                        )
        
        return socials
        
