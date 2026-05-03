from datetime import timedelta

from solidago.poll import *
from solidago.poll import User
from solidago.poll_functions import PollFunction
from solidago.primitives.datastructure.filtered_table import SelectLast
from solidago.primitives.decay import Decay

import logging
logger = logging.getLogger(__name__)


class Follows(PollFunction):
    default_follows: dict[str, float] = dict(follow=1.)

    def __init__(self,
        follows: dict[str, float] | None = None, 
        default_representative: tuple[str, dict] | None = None,
        decay: Decay | tuple[str, dict] | None = None,
        follow_lifetime: int | None = None,
        max_workers: int | None = None,
        receiver: User | None = None,
        time: int | None = None,
    ):
        """ decay is directly in added to BaseVolumes because it also depends on self.follows """
        super().__init__(max_workers)
        self.follows = self.default_follows if follows is None else follows
        self.default_representative = default_representative or ("Representative", dict())
        import solidago, solidago.primitives.decay as d
        self.decay = solidago.load(decay, d, Decay, d.NoDecay())
        self.follow_lifetime = follow_lifetime or timedelta(weeks=52*3).seconds
        self.receiver = receiver
        self.time = time

    def fn(self, users: Users, socials: Socials) -> Users:
        if self.receiver is None:
            self.log_warning("No receiver for Follows. Identity used instead.")
            return users
        follows = socials.filters(by=self.receiver.name, kind=self.follows.keys())
        councillors = users.filters(follows.get_column("to"))
        volumes = councillors.names().map(lambda c: follows.get(SelectLast("date"), to=c.name)["weight"])
        dates = councillors.names().map(lambda c: follows.get(SelectLast("date"), to=c.name)["date"])
        volumes *= self.decay(self.time - dates.to_numpy(), self.follow_lifetime)
        councillors = councillors.assign(volume=volumes)
        representative_names = councillors\
            .get_column("representative")\
            .map(lambda x: self.default_representative if x == "default" else x)
        return councillors.assign(representative=representative_names)