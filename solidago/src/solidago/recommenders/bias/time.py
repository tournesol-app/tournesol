from abc import abstractmethod
from datetime import datetime, timedelta

import numpy as np

from solidago.poll import *
from .bias import BallotBiasing


class TimeDecay(BallotBiasing):
    default_default_lifetime: dict = dict(weeks=1)

    def __init__(self,
        default_lifetime: dict | None = None,
        lifetime_bias: float = 0.,
        time: datetime | None = None
    ):
        default_lifetime = default_lifetime or self.default_default_lifetime
        self.default_lifetime = timedelta(**default_lifetime)
        self.lifetime_bias = lifetime_bias
        self.time = datetime.now() if time is None else time

    @abstractmethod
    def decay(self, date: int, lifetime: int) -> float:
        raise NotImplementedError

    def __call__(self, entities: Entities, ballot: Scores) -> Scores:
        biased_ballot = Scores(keynames=["entity_name"])
        for score in ballot:
            entity = entities[score["entity_name"]]
            date, lifetime = entity["date"], score["lifetime"]
            biased_score = score * self.decay(date, lifetime)
            assert isinstance(biased_score, Score)
            kwargs = dict(entity_name=entity.name, date=date, lifetime=lifetime)
            biased_ballot.append(biased_score, **kwargs)
        return biased_ballot
    
    
class QuadraticTimeDecay(TimeDecay):
    def decay(self, date: int, lifetime: int) -> float:
        """ date and lifetime must be given in seconds """
        age = date - self.time.second
        decay = lifetime / (age**2 + lifetime**2)
        if lifetime != 0 and lifetime != self.default_lifetime.seconds:
            log = np.log(1 + lifetime / self.default_lifetime.seconds)
            decay *= np.power(log, self.lifetime_bias)
        return decay