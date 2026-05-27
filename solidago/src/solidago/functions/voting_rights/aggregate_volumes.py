from typing import Iterable

import numpy as np

from solidago.functions.poll_function import PollFunction
from solidago.poll import *


class AggregateVolumes(PollFunction):
    def __init__(self, volume_names: Iterable[str]=("follow_volume", "like_volume", "mention_volume")):
        self.volume_names = volume_names

    def fn(self, voting_rights: VotingRights) -> VotingRights:
        volumes = 0
        for volume_name in self.volume_names:
            volumes = volumes + voting_rights(volume_name, 0)
        return voting_rights.add_columns(voting_right=volumes)