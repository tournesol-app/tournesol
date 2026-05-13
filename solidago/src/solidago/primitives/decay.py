from abc import abstractmethod
from numpy.typing import NDArray

import numpy as np

from solidago.primitives.time import Duration, DurationInput


class Decay:
    @abstractmethod
    def __call__(self, ages: NDArray, lifetimes: NDArray | float) -> NDArray:
        raise NotImplemented


class NoDecay(Decay):
    def __call__(self, ages: NDArray, lifetimes: NDArray | float) -> NDArray:
        return np.ones_like(ages)


class QuadraticDecay(Decay):
    def __call__(self, ages: NDArray, lifetimes: NDArray | float) -> NDArray:
        return lifetimes**2 / (ages**2 + lifetimes**2)


class LifetimeBiasedDecay(Decay):
    def __init__(self, lifetime_bias: float, default_lifetime: DurationInput):
        self.default_lifetime = Duration(default_lifetime)
        self.lifetime_bias = lifetime_bias

    def __call__(self, ages: NDArray, lifetimes: NDArray | float) -> NDArray:
        """ All values must be in seconds """
        decay = self.default_lifetime.seconds * lifetimes / (ages**2 + lifetimes**2)
        if self.lifetime_bias == 0:
            return decay
        log = np.log(1 + lifetimes / self.default_lifetime.seconds)
        return decay * np.power(log, self.lifetime_bias)
