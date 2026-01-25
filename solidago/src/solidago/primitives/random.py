from abc import abstractmethod
from copy import deepcopy
from typing import Iterable, Type, Union
from numpy.typing import NDArray

import numpy as np

from solidago import primitives


class Distribution:
    @abstractmethod
    def sample(self, n_samples: int = 1) -> NDArray:
        raise NotImplemented
    
    @classmethod
    def load(cls, distribution: Union["Distribution", tuple, list]) -> "Distribution":
        if isinstance(distribution, Distribution):
            return distribution
        assert isinstance(distribution, (list, tuple)), distribution
        assert len(distribution) == 2, distribution
        assert isinstance(distribution[0], (str, Type)), distribution
        assert isinstance(distribution[1], dict), distribution
        cls, kwargs = distribution
        distribution = getattr(primitives.random, cls)(**kwargs)
        assert isinstance(distribution, Distribution)
        return distribution
    
    def __repr__(self) -> str:
        if self.__dict__:
            key_values = [f"{key}={value}" for key, value in self.__dict__.items()]
            return type(self).__name__ + f"({', '.join(key_values)})"
        return type(self).__name__

class Deterministic(Distribution):
    def __init__(self, value: bool | int | float | NDArray):
        assert isinstance(value, (bool, int, float, NDArray))
        self.value = value

    def sample(self, n_samples: int = 1) -> NDArray:
        assert isinstance(n_samples, int), n_samples
        return np.array([deepcopy(self.value) for _ in range(n_samples)])

class Bernoulli(Distribution):
    def __init__(self, p: float):
        assert p >= 0.0 and p <= 1.0
        self.p = p
    
    def sample(self, n_samples: int = 1) -> NDArray:
        return np.random.random(n_samples) < self.p

class Normal(Distribution):
    def __init__(self, 
        dimension: int | None = None,
        mean: float | NDArray = 0.0,
        std: float | NDArray = 1.0,
    ):
        self.dimension = dimension or np.array(mean).size
        assert isinstance(self.dimension, int)
        self.mean = (np.zeros(self.dimension) + mean) if isinstance(mean, float) else mean
        self.std = (np.zeros(self.dimension) + std) if isinstance(mean, float) else mean

    def sample(self, n_samples: int = 1) -> NDArray:
        if self.dimension == 1:
            return np.random.normal(self.mean, self.std, n_samples)
        if n_samples == 1:
            return np.random.normal(self.mean, self.std, self.dimension)
        return np.random.normal(self.mean, self.std, (self.dimension, n_samples))

class Zipf(Distribution):
    def __init__(self, power_decay: float):
        assert power_decay > 1.0
        self.power_decay = power_decay
    
    def sample(self, n_samples: int = 1) -> NDArray:
        return np.random.zipf(self.power_decay, n_samples)

class Poisson(Distribution):
    def __init__(self, mean: float):
        assert mean >= 0.0
        self.mean = mean
    
    def sample(self, n_samples: int = 1) -> NDArray:
        return np.random.poisson(self.mean, n_samples)

class Gamma(Distribution):
    def __init__(self, shape: float, scale: float = 1.0):
        assert shape > 0
        assert scale > 0
        self.shape = shape
        self.scale = scale
    
    def sample(self, n_samples: int = 1) -> NDArray:
        return np.random.gamma(self.shape, self.scale, n_samples)
    
class Uniform(Distribution):
    def __init__(self, min: float = 0.0, max: float = 1.0):
        assert min <= max
        self.min, self.max = min, max
    
    def sample(self, n_samples: int = 1) -> NDArray:
        return np.random.uniform(self.min, self.max, n_samples)

class Multinomial(Distribution):
    def __init__(self, probabilities: Iterable, values: list[str] | None):
        self.probabilities = np.array(list(probabilities))
        self.values = values or [str(i) for i in range(len(self.probabilities))]
        assert all(self.probabilities >= 0)
        assert self.probabilities.sum() == 1
        assert len(self.values) == len(self.probabilities)
    
    def sample(self, n_samples = 1) -> list[str]:
        dim = len(self.probabilities)
        return [
            self.values[(np.random.multinomial(1, self.probabilities) * np.arange(dim)).sum()]
            for i in range(n_samples)
        ]

class Add(Distribution):
    def __init__(self, subdistributions: list):
        self.subdistributions = [Distribution.load(d) for d in subdistributions]
    
    def sample(self, n_samples: int = 1) -> NDArray:
        if not self.subdistributions:
            return np.zeros(n_samples)
        values = self.subdistributions[0].sample(n_samples)
        for subdistribution in self.subdistributions[1:]:
            values += subdistribution.sample(n_samples)
        return values
