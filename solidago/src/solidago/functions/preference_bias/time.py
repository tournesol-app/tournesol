import numpy as np

from solidago.functions.preference_bias.bias import PreferenceBias
from solidago.primitives.decay import Decay, QuadraticDecay
from solidago.poll import *
from solidago.primitives.time import Date, DateInput, Duration


class TimeDecay(PreferenceBias):
    default_decay: QuadraticDecay = QuadraticDecay(2.)

    def __init__(self,
        decay: Decay | tuple[str, dict] | None = None,
        date: DateInput | None = None,
    ):
        super().__init__(date)
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, self.default_decay)

    def multipliers(self, poll: Poll, scores: Scores) -> Scores:
        date = Date.now() if self.date is None else self.date
        scores_dates = np.array(Date(d).seconds for d in scores("date"))
        lifetimes = np.array(Duration(d).seconds for d in scores("lifetime"))
        decay = self.decay(date.seconds - scores_dates, lifetimes)
        return Scores(value=decay)