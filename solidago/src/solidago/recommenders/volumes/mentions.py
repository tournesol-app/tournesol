from functools import reduce
from datetime import timedelta

import numpy as np

from solidago.poll.poll import Poll
from solidago.poll.poll_tables import User, Users
from solidago.primitives.datastructure import Contains, After

from .volumes import VolumeBiasing


class Mentions(VolumeBiasing):
    def __init__(self, 
        mention_volume: float = .5,
        relative_max_volume: float = .2,
        age_cutoff: dict[str, int] | int | None = None
    ):
        """
        Parameters
        ----------
        mention_volume: float
            volume of a user that mentions the receiver
            Their actual volume may be larger if the user is already a councillor
            It may be lower if too many noncouncillors mention the receiver
        relative_max_volume: float
            The total added volume through mentions must be a relative fraction
            of explicitly defined councillors, to guarantee receiver control
            over the volumes they allocate
        age_cutoff: dict[str, int] | int | None = None
            Could be e.g. dict(weeks=1)
            Mentions that are older than age_cutoff will be discarded
            Default value is 52 weeks
        """
        self.mention_volume = mention_volume
        self.relative_max_volume = relative_max_volume
        if isinstance(age_cutoff, int):
            self.age_cutoff = age_cutoff
        else:
            self.age_cutoff = timedelta(**age_cutoff or dict(weeks=52)).seconds

    def __call__(self, poll: Poll, receiver: User, time: float, councillors: Users) -> Users:
        min_date = time - self.age_cutoff
        entities = poll.entities.filters(mentions=Contains(receiver.name), date=After(min_date))
        mentioners = reduce(lambda acc, e: acc | set(e["authors"]), entities, set())
        
        missing_volumes = councillors.names()\
            .map(lambda c: max(0, self.mention_volume - c["volume"]) if c in mentioners else 0)\
            .to_numpy(np.float64)
        others = {n for n in mentioners if n not in councillors}
        missing_volume = missing_volumes.sum() + len(others) * self.mention_volume
        councillor_volume = councillors.get_column("volume").to_numpy(np.float64).sum()
        multiplier = min(1., self.relative_max_volume * councillor_volume / missing_volume)
        volumes = councillors.get_column("volume").to_numpy(np.float64) \
            + missing_volumes * multiplier
        councillors = councillors.assign(volume=volumes)
        noncouncillors = poll.users.filters(others)\
            .assign(volume=self.mention_volume * multiplier)

        return councillors | noncouncillors