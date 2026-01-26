from abc import abstractmethod
from typing import Union

import numpy as np

from solidago.poll import *
from solidago.primitives.random import Distribution

class Rate:
    @abstractmethod
    def __call__(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> Rating:
        raise NotImplemented

    @classmethod
    def load(cls, rate: Union["Rate", list, tuple], honest: Union["Rate", list, tuple] | None = None):
        if isinstance(rate, Rate):
            return rate
        assert isinstance(rate, (list, tuple)) and len(rate) == 2, rate
        classname, kwargs = rate
        from solidago.generators import ratings
        assert hasattr(ratings, classname), classname
        cls = getattr(ratings, classname)
        if honest and "honest" in cls.__init__.__annotations__:
            kwargs["honest"] = Rate.load(honest)
        return cls(**kwargs)
    
    def __repr__(self):
        t = ".".join(str(type(self)).split(".")[2:])[:-2]
        kwargs = ", ".join([f"{k}={v}" for k, v in self.__dict__.items()])
        return f"{t}({kwargs})"


class Deterministic(Rate):
    def __call__(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> Rating:
        value = user.vector @ entity.vector / np.sqrt(user.vector.size)
        if hasattr(user, "multiplier"):
            value *= user.multiplier
        if hasattr(user, "translation"):
            value += user.translation
        assert isinstance(value, float)
        return Rating(value)


class Negate(Rate):
    def __init__(self, honest: Union["Rate", list, tuple] | None = None):
        self.honest = Rate.load(honest)

    def __call__(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> Rating:
        value = self.honest(rating, user, entity, public, criterion).value
        assert isinstance(- value, float)
        return Rating(- value)


class Noisy(Rate):
    def __init__(self, distribution: Distribution | list | tuple):
        self.distribution = Distribution.load(distribution)

    def __call__(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> Rating:
        value = Deterministic()(rating, user, entity, public, criterion).value
        assert isinstance(value, float)
        return Rating(value + self.distribution.sample()[0])
