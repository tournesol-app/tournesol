from typing import Self

import numpy as np

from solidago.poll import *
from .bias import PreferenceBias


class SemanticBias(PreferenceBias):
    def __init__(self, receiver: User | None = None, bias: float = 1.):
        self.receiver = receiver
        self.bias = bias

    def multipliers(self, poll: Poll, scores: Scores) -> Scores:
        assert self.receiver is not None, f"Ran {type(self).__name__} with receiver"
        entities = poll.entities.filters(scores("entity_names"))
        unit = self.receiver.vector / np.sqrt((self.receiver.vector**2).sum())
        unit_embeddings = entities.vectors / np.sqrt((entities.vectors**2).sum(axis=0))
        multipliers = np.power(1 + unit @ unit_embeddings, self.bias)
        return Scores(value=multipliers)