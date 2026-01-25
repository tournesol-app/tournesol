from abc import abstractmethod
from typing import Union

import numpy as np

from solidago.poll import *
from solidago.primitives.random import Distribution

class Assess:
    @abstractmethod
    def __call__(self, assessment: Assessment, user: User, entity: Entity, public: bool, criterion: str) -> Assessment:
        raise NotImplemented

    @classmethod
    def load(cls, assess: Union["Assess", list, tuple], honest: Union["Assess", list, tuple] | None = None):
        if isinstance(assess, Assess):
            return assess
        assert isinstance(assess, (list, tuple)) and len(assess) == 2, assess
        classname, kwargs = assess
        from solidago.generators import assessments
        assert hasattr(assessments, classname), classname
        cls = getattr(assessments, classname)
        if honest and "honest" in cls.__init__.__annotations__:
            kwargs["honest"] = Assess.load(honest)
        return cls(**kwargs)
    
    def __repr__(self):
        t = ".".join(str(type(self)).split(".")[2:])[:-2]
        kwargs = ", ".join([f"{k}={v}" for k, v in self.__dict__.items()])
        return f"{t}({kwargs})"


class Deterministic(Assess):
    def __call__(self, assessment: Assessment, user: User, entity: Entity, public: bool, criterion: str) -> Assessment:
        value = user.vector @ entity.vector / np.sqrt(user.vector.size)
        if hasattr(user, "multiplier"):
            value *= user.multiplier
        if hasattr(user, "translation"):
            value += user.translation
        assert isinstance(value, float)
        return Assessment(value)


class Negate(Assess):
    def __init__(self, honest: Union["Assess", list, tuple] | None = None):
        self.honest = Assess.load(honest)

    def __call__(self, assessment: Assessment, user: User, entity: Entity, public: bool, criterion: str) -> Assessment:
        value = self.honest(assessment, user, entity, public, criterion).value
        assert isinstance(- value, float)
        return Assessment(- value)


class Noisy(Assess):
    def __init__(self, distribution: Distribution | list | tuple):
        self.distribution = Distribution.load(distribution)

    def __call__(self, assessment: Assessment, user: User, entity: Entity, public: bool, criterion: str) -> Assessment:
        value = Deterministic()(assessment, user, entity, public, criterion).value
        assert isinstance(value, float)
        return Assessment(value + self.distribution.sample()[0])
