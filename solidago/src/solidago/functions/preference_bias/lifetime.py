from numpy.typing import NDArray

import numpy as np

from solidago.primitives.time import DurationInput, Duration
from solidago.poll import *
from .bias import WeightPreservingBias


class LifetimeBias(WeightPreservingBias):
    def __init__(self, 
        default_preferred_lifetime: DurationInput | None = None, 
        default_lifetime_bias: float = 1., 
        *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.default_preferred_lifetime = None
        if default_preferred_lifetime is not None:
            self.default_preferred_lifetime = Duration(default_preferred_lifetime)
        self.default_lifetime_bias = default_lifetime_bias
    
    def _multipliers(self,  # type: ignore
        scores: Scores, 
        users: Users,
        entities: Entities,
    ) -> tuple[NDArray, NDArray | float, NDArray | float]:
        assert self.username is not None, f"Ran {type(self).__name__} without receiver"
        user = users[self.username]
        pref_lifetime = user.get("preferred_lifetime", self.default_preferred_lifetime)
        lifetime_bias = user.get("lifetime_bias", self.default_lifetime_bias)
        lifetimes = entities.filters(scores("entity_names"))("lifetime")
        discrepancy = np.power(np.log(lifetimes / pref_lifetime), 2)
        return np.power(1 + discrepancy, - lifetime_bias), 0., 0.