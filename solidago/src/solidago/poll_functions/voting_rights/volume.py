from typing import Iterable

import numpy as np

from solidago.poll_functions.poll_function import PollFunction
from solidago.poll import *


class AggregateVolumes(PollFunction):
    def __init__(self, volume_names: Iterable[str]=("follow_volume", "like_volume", "mention_volume")):
        self.volume_names = volume_names

    def fn(self, users: Users) -> tuple[Users, VotingRights]:
        volumes = np.zeros(len(users))
        for name in self.volume_names:
            volumes += users(name, 0)
        voting_rights = VotingRights(dict(username=users.names(), volume=volumes), keynames=["username"])
        return users.assign(volume=volumes), voting_rights