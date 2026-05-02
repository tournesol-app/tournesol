from abc import abstractmethod
from datetime import timedelta
from numpy.typing import NDArray

import numpy as np


class Decay:
    @abstractmethod
    def __call__(self, age: NDArray, lifetime: NDArray | float) -> NDArray:
        raise NotImplemented


class NoDecay(Decay):
    def __call__(self, age: NDArray, lifetime: NDArray | float) -> NDArray:
        return np.ones_like(age)


class QuadraticDecay(Decay):
    def __call__(self, age: NDArray, lifetime: NDArray | float) -> NDArray:
        return lifetime**2 / (age**2 + lifetime**2)


class LifetimeBiasedDecay(Decay):
    def __init__(self, lifetime_bias: float, default_lifetime: dict[str, int]):
        self.default_lifetime = timedelta(**default_lifetime).seconds
        self.lifetime_bias = lifetime_bias

    def __call__(self, age: NDArray, lifetime: NDArray | float) -> NDArray:
        decay = lifetime / (age**2 + lifetime**2)
        if self.lifetime_bias == 0:
            return decay
        log = np.log(1 + lifetime / self.default_lifetime)
        return decay * np.power(log, self.lifetime_bias)
