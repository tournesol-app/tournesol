from datetime import datetime

from solidago.functions.preference_bias.bias import PreferenceBias
from solidago.primitives.decay import Decay
from solidago.poll import *


class TimeDecay(PreferenceBias):
    def __init__(self,
        decay: Decay | tuple[str, dict] | None = None,
        time: datetime | str | None = None,
    ):
        super().__init__(time)
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, d.QuadraticDecay())

    def multipliers(self, poll: Poll, scores: Scores) -> Scores:
        time = (datetime.now() if self.time is None else self.time).second
        decay = self.decay(time - scores("date"), scores("lifetime"))
        return Scores(value=decay)