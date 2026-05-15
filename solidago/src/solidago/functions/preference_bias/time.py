from numpy.typing import NDArray

import numpy as np

from solidago.functions.preference_bias.bias import PreferenceBias
from solidago.primitives.decay import Decay, QuadraticDecay
from solidago.poll import *
from solidago.primitives.time import Date, DateInput, Duration, DurationInput


class TimeDecay(PreferenceBias):
    default_decay: QuadraticDecay = QuadraticDecay(2.)
    default_default_lifetime: Duration = Duration(days=1)

    def __init__(self,
        decay: Decay | tuple[str, dict] | None = None,
        default_lifetime: DurationInput | None = None,
        date: DateInput | None = None,
        max_workers: int | None = None,
    ):
        super().__init__(date, max_workers)
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, self.default_decay)
        self.default_lifetime = self.default_default_lifetime
        if default_lifetime is not None:
            self.default_lifetime = Duration(default_lifetime)

    def _multipliers(self, # type: ignore
        scores: Scores
    ) -> tuple[NDArray, NDArray | float, NDArray | float]: 
        date = Date.now() if self.date is None else self.date
        ages = np.array([(date - Date(d)).seconds for d in scores("date")])
        lifetimes = self.default_lifetime.seconds
        if "lifetime" in scores.columns:
            lifetimes = np.array([Duration(d).seconds for d in scores("lifetime")])
        return self.decay(ages, lifetimes), 0., 0.