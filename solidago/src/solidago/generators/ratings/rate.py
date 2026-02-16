from abc import abstractmethod
from typing import Any, Union

import numpy as np

from solidago.poll import *
from solidago.primitives.random import Distribution

class Rate:
    def __call__(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str):
        rating["value"] = self.sample_value(rating, user, entity, public, criterion)

    @abstractmethod
    def sample_value(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> float:
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
    def sample_value(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> float:
        value = user.vector @ entity.vector / np.sqrt(user.vector.size)
        if "multiplier" in user:
            value *= user["multiplier"]
        if "translation" in user:
            value += user["translation"]
        assert isinstance(value, float)
        return value


class Negate(Rate):
    def __init__(self, honest: Union["Rate", list, tuple]):
        self.honest = Rate.load(honest)

    def sample_value(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> float:
        return - self.honest.sample_value(rating, user, entity, public, criterion)


class Noisy(Rate):
    def __init__(self, distribution: Distribution | tuple[str, dict[str, Any]]):
        self.distribution = Distribution.load(distribution)

    def sample_value(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> float:
        value = Deterministic().sample_value(rating, user, entity, public, criterion)
        return value + self.distribution.sample()[0]
