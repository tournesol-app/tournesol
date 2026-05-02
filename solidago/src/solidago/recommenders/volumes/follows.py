from datetime import timedelta

import numpy as np

from solidago.primitives.decay import Decay
from solidago.poll import *
from .volumes import BaseVolumes

class Follows(BaseVolumes):
    default_follows: dict[str, float] = dict(follow=1.)

    def __init__(self,
        follows: dict[str, float] | None = None, 
        default_representative: tuple[str, dict] | None = None,
        decay: Decay | tuple[str, dict] | None = None,
        follow_lifetime: int | None = None,
    ):
        """ decay is directly in added to BaseVolumes because it also depends on self.follows """
        self.follows = self.default_follows if follows is None else follows
        self.default_representative = default_representative or ("Representative", dict())
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, d.NoDecay())
        self.follow_lifetime = follow_lifetime or timedelta(weeks=52*3).seconds

    def __call__(self, poll: Poll, receiver: User, time: float) -> Users:
        follows = poll.socials.filters(by=receiver.name, kind=self.follows.keys())
        councillors = poll.users.filters(follows.get_column("to"))
        volumes = councillors.names().map(lambda c: follows.get("last", to=c.name)["weight"])
        dates = councillors.names().map(lambda c: follows.get("last", to=c.name)["date"])
        volumes *= self.decay(time - dates.to_numpy(np.float64), self.follow_lifetime)
        councillors = councillors.assign(volume=volumes)
        representative_names = councillors\
            .get_column("representative")\
            .map(lambda x: self.default_representative if x == "default" else x)
        return councillors.assign(representative=representative_names)