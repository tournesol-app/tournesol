from abc import abstractmethod
from typing import Any, Union

import numpy as np

from solidago.poll import *
from solidago.primitives.random import Distribution

class Rate:
    def __call__(self, 
        rating: Rating, 
        user: User, 
        entity: Entity, 
        public: bool, 
        criterion: str
    ) -> dict[str, Any]:
        return dict(value=self.sample_value(rating, user, entity, public, criterion))

    @abstractmethod
    def sample_value(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> float:
        raise NotImplemented
    
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
        import solidago
        self.honest = solidago.load(honest, solidago.generators.ratings)

    def sample_value(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> float:
        return - self.honest.sample_value(rating, user, entity, public, criterion)


class Noisy(Rate):
    def __init__(self, distribution: Distribution | tuple[str, dict[str, Any]]):
        import solidago
        self.distribution = solidago.load(distribution, solidago.random)

    def sample_value(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> float:
        value = Deterministic().sample_value(rating, user, entity, public, criterion)
        return value + self.distribution.sample()[0]
