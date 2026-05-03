import numpy as np

from solidago.poll.poll import Poll

from .bias import WeightPreservingBias


class LifetimeBias(WeightPreservingBias):
    def __init__(self, lifetime: int, bias: float):
        assert lifetime >= 1 and bias >= 0
        self.lifetime = lifetime
        self.bias = bias

    def multiplier(self, entity_name: str, poll: Poll) -> np.float64:
        lifetime = poll.entities[entity_name]["lifetime"]
        discrepancy = np.power(np.log(lifetime / self.lifetime), 2)
        return np.power(1 + discrepancy, - self.bias)