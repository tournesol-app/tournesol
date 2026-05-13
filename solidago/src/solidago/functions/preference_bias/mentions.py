from typing import Self

import numpy as np

from solidago.poll import *
from .bias import PreferenceBias


class MentionBias(PreferenceBias):
    def __init__(self, receiver: User | None = None, multiplier: float = 5.):
        self.receiver = receiver
        self.multiplier = multiplier

    def multipliers(self, poll: Poll, scores: Scores) -> Scores:
        assert self.receiver is not None, f"Ran {type(self).__name__} without receiver"
        entities = poll.entities.filters(scores("entity_names"))
        mentions = np.array(self.receiver.name in m for m in entities("mentions"))
        return Scores(value=1 + mentions * self.multiplier)