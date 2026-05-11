from typing import Self
from numpy.typing import NDArray

import numpy as np

from solidago.poll import *
from .bias import PreferenceBias, WeightPreservingBias


class SemanticBias(PreferenceBias):
    def __init__(self, vector: NDArray, bias: float = 1.):
        self.vector = vector
        self.bias = bias
    
    def customize(self, user: User, time: int | None = None) -> Self:
        self.vector = user.vector
        return self 

    def multiplier(self, poll: Poll, scores: Scores) -> Scores:
        entities = poll.entities.filters(scores("entity_names"))
        assert isinstance(entities, Entities)
        unit = self.vector / np.sqrt((self.vector**2).sum())
        unit_embeddings = entities.vectors / np.sqrt((entities.vectors**2).sum(axis=0))
        multipliers = np.power(1 + unit @ unit_embeddings, self.bias)
        return Scores(value=multipliers)