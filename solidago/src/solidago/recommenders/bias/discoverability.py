import numpy as np

from solidago.poll.poll import Poll

from .bias import WeightPreservingBias


class Discoverability(WeightPreservingBias):
    def __init__(self, popularity_indicator: str, min: int, bias: float):
        assert min >= 1
        self.popularity_indicator = popularity_indicator
        self.min = min
        self.bias = bias

    def multiplier(self, entity_name: str, poll: Poll) -> np.float64:
        n = poll.entities[entity_name][self.popularity_indicator]
        return np.power(np.log(self.min) / np.log(self.min + n), self.bias)