from datetime import datetime, timedelta

import numpy as np

from solidago.functions.poll_function import PollFunction
from solidago.primitives.decay import Decay
from solidago.poll import *
from solidago.primitives.time import Date, DateInput, Duration, DurationInput


class Follows(PollFunction):
    default_follows: dict[str, float] = dict(follow=1.)
    default_follow_lifetime: Duration = Duration(weeks=52.*3)

    def __init__(self,
        follows: dict[str, float] | None = None, 
        decay: Decay | tuple[str, dict] | None = None,
        follow_lifetime: DurationInput | None = None,
        receiver: User | None = None,
        date: DateInput | None = None,
    ):
        """ decay is directly in added to BaseVolumes because it also depends on self.follows """
        self.follows = self.default_follows if follows is None else follows
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, d.NoDecay())
        fl = follow_lifetime
        self.follow_lifetime = self.default_follow_lifetime if fl is None else Duration(fl)
        self.receiver = receiver
        self.date = None if date is None else Date(date)

    def fn(self, users: Users, socials: Socials) -> Users:
        if self.receiver is None:
            self.log_warning("Follows without receiver. Identity used instead.")
            return users.assign(follow_volume=0)
        follows = socials.filters(by=self.receiver.name, kind=self.follows.keys())
        councillors = users.filters(follows("to"))
        follow_volumes = councillors.names().map(lambda c: follows.get(to=c)["weight"])
        dates = councillors.names().map(lambda c: Date(follows.get(to=c)["date"]).seconds)
        date = Date.now() if self.date is None else self.date
        ages = date.seconds - dates.to_numpy()
        follow_volumes *= self.decay(ages, self.follow_lifetime.seconds)
        return users.assign(follow_volumes=follow_volumes)