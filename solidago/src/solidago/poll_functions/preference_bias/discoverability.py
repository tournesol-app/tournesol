import numpy as np

from solidago.poll import *
from .bias import WeightPreservingBias


class Discoverability(WeightPreservingBias):
    def __init__(self, popularity_indicator: str, min: int, bias: float):
        assert min >= 1
        self.popularity_indicator = popularity_indicator
        self.min = min
        self.bias = bias

    def multiplier(self, poll: Poll, scores: Scores) -> Scores:
        entities = poll.entities.filters(scores("entity_names"))
        assert isinstance(entities, Entities)
        popularities = entities(self.popularity_indicator)
        values = np.power(np.log(self.min) / np.log(self.min + popularities), self.bias)
        return Scores(value=values)