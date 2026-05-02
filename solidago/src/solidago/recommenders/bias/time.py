from datetime import datetime, timedelta

from solidago.primitives.decay import Decay
from solidago.poll import *
from .bias import BallotBiasing


class TimeDecay(BallotBiasing):
    default_default_lifetime: dict = dict(weeks=1)

    def __init__(self,
        default_lifetime: dict | None = None,
        lifetime_bias: float = 0.,
        time: datetime | None = None,
        decay: Decay | tuple[str, dict] | None = None,
    ):
        default_lifetime = default_lifetime or self.default_default_lifetime
        self.default_lifetime = timedelta(**default_lifetime)
        self.lifetime_bias = lifetime_bias
        self.time = datetime.now() if time is None else time
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, d.QuadraticDecay())

    def __call__(self, poll: Poll, ballot: Scores) -> Scores:
        biased_ballot = Scores(keynames=["entity_name"])
        for score in ballot:
            entity = poll.entities[score["entity_name"]]
            date, lifetime = entity["date"], score["lifetime"]
            biased_score = score * self.decay(date, lifetime)
            assert isinstance(biased_score, Score)
            kwargs = dict(entity_name=entity.name, date=date, lifetime=lifetime)
            biased_ballot.append(biased_score, **kwargs)
        return biased_ballot
