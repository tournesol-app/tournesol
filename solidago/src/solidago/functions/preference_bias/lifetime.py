import numpy as np

from solidago.primitives.time import DurationInput, Duration
from solidago.poll import *
from .bias import WeightPreservingBias


class LifetimeBias(WeightPreservingBias):
    def __init__(self, preferred_lifetime: DurationInput | None = None, bias: float = 1.):
        self.preferred_lifetime = None
        if preferred_lifetime is not None:
            self.preferred_lifetime = Duration(preferred_lifetime)
        self.bias = bias
    
    def customize(self, user: User, date=None):
        if "preferred_lifetime" in user:
            self.preferred_lifetime = user["preferred_lifetime"]
        if "lifetime_bias" in user:
            self.bias = user["lifetime_bias"]

    def multipliers(self, poll: Poll, scores: Scores) -> Scores:
        assert self.preferred_lifetime is not None, \
            f"Ran {type(self).__name__} without receiver preferred lifetime"
        entities = poll.entities.filters(scores("entity_names"))
        lifetimes = entities("lifetime")
        discrepancy = np.power(np.log(lifetimes / self.preferred_lifetime), 2)
        multipliers = np.power(1 + discrepancy, - self.bias)
        return Scores(value=multipliers)