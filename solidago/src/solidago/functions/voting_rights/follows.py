from datetime import datetime, timedelta

import numpy as np

from solidago.functions.poll_function import PollFunction
from solidago.primitives.decay import Decay
from solidago.poll import *


class Follows(PollFunction):
    default_follows: dict[str, float] = dict(follow=1.)

    def __init__(self,
        follows: dict[str, float] | None = None, 
        decay: Decay | tuple[str, dict] | None = None,
        follow_lifetime: int | None = None,
        receiver: User | None = None,
        time: int | None = None,
    ):
        """ decay is directly in added to BaseVolumes because it also depends on self.follows """
        self.follows = self.default_follows if follows is None else follows
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, d.NoDecay())
        self.follow_lifetime = follow_lifetime or timedelta(weeks=52*3).seconds
        self.receiver = receiver
        self.time = time

    def fn(self, users: Users, socials: Socials) -> Users:
        if self.receiver is None:
            self.log_warning("Follows without receiver. Identity used instead.")
            return users.assign(follow_volume=0)
        follows = socials.filters(by=self.receiver.name, kind=self.follows.keys())
        councillors = users.filters(follows("to"))
        follow_volumes = councillors.names().map(lambda c: follows.get(to=c)["weight"])
        dates = councillors.names().map(lambda c: follows.get(to=c)["date"])
        time = self.time or datetime.now().second
        follow_volumes *= self.decay(time - dates.to_numpy(np.float64), self.follow_lifetime)
        return users.assign(follow_volumes=follow_volumes)