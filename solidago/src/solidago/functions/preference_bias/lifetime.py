from typing import Self
from datetime import timedelta

import numpy as np

from solidago.poll import *
from .bias import WeightPreservingBias


class LifetimeBias(WeightPreservingBias):
    def __init__(self, lifetime: int | dict[str, int] | None = None, bias: float = 1.):
        if not isinstance(lifetime, int):
            lifetime = dict(weeks=1) if lifetime is None else lifetime
            lifetime = timedelta(**lifetime).seconds
        assert lifetime >= 1 and bias >= 0
        self.lifetime = lifetime
        self.bias = bias
    
    def customize(self, user: User, time: int | None = None) -> Self:
        self.lifetime, self.bias = user["lifetime_preference"], user["lifetime_bias"]
        return self 

    def multipliers(self, poll: Poll, scores: Scores) -> Scores:
        entities = poll.entities.filters(scores("entity_names"))
        lifetimes = entities("lifetime")
        discrepancy = np.power(np.log(lifetimes / self.lifetime), 2)
        multipliers = np.power(1 + discrepancy, - self.bias)
        return Scores(value=multipliers)