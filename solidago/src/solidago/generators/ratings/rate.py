from abc import abstractmethod
from typing import Any, Union

import numpy as np

from solidago.poll import *
from solidago.primitives.random import Distribution

class Rate:
    def __init__(self, root_law_name: str = "Gaussian", root_law_arg: Any = 1.0):
        self.root_law_name = root_law_name
        self.root_law_arg =root_law_arg

    def __call__(self, 
        rating: Rating, 
        user: User, 
        entity: Entity, 
        public: bool, 
        criterion: str
    ) -> dict[str, Any]:
        return dict(
            value=self.sample_value(rating, user, entity, public, criterion), 
            generation_root_law=self.root_law_name, 
            generation_root_law_arg=self.root_law_arg
        )

    @abstractmethod
    def sample_value(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> float:
        raise NotImplemented
    
    def __repr__(self):
        t = ".".join(str(type(self)).split(".")[2:])[:-2]
        kwargs = ", ".join([f"{k}={v}" for k, v in self.__dict__.items()])
        return f"{t}({kwargs})"


class Deterministic(Rate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
        honest = solidago.load(honest, solidago.generators.ratings)
        assert isinstance(honest, Rate)
        super().__init__(honest.root_law_name, honest.root_law_arg)
        self.honest = honest

    def sample_value(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> float:
        return - self.honest.sample_value(rating, user, entity, public, criterion)


class Noisy(Rate):
    def __init__(self, distribution: Distribution | tuple[str, dict[str, Any]], *args, **kwargs):
        import solidago
        super().__init__(*args, **kwargs)
        distribution = solidago.load(distribution, solidago.random)
        assert isinstance(distribution, Distribution)
        self.distribution = distribution

    def sample_value(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> float:
        value = Deterministic().sample_value(rating, user, entity, public, criterion)
        return value + self.distribution.sample()[0]
