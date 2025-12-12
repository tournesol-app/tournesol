from abc import abstractmethod
from typing import Union

import numpy as np

from solidago.poll import *


class Compare:
    @abstractmethod
    def __call__(self, 
        comparison: Comparison, 
        user: User, left: Entity, right: Entity, 
        left_public: bool, right_public, 
        criterion: str
    ) -> Comparison:
        raise NotImplemented

    @classmethod
    def load(cls, compare: Union["Compare", list, tuple], honest: Union["Compare", list, tuple] | None = None):
        if isinstance(compare, Compare):
            return compare
        assert isinstance(compare, (list, tuple)) and len(compare) == 2
        classname, kwargs = compare
        from solidago.generators import comparisons
        assert hasattr(comparisons, classname), classname
        cls = getattr(comparisons, classname)
        if honest and "honest" in cls.__init__.__annotations__:
            kwargs["honest"] = Compare.load(honest)
        return cls(**kwargs)
    
    def __repr__(self):
        t = ".".join(str(type(self)).split(".")[2:])[:-2]
        kwargs = ", ".join([f"{k}={v}" for k, v in self.__dict__.items()])
        return f"{t}({kwargs})"

class Deterministic(Compare):
    def __call__(self, 
        comparison: Comparison, 
        user: User, left: Entity, right: Entity, 
        left_public: bool, right_public, 
        criterion: str
    ) -> Comparison:
        value = user.vector @ (right.vector - left.vector) / np.sqrt(user.vector.size)
        if hasattr(user, "multiplier"):
            value *= user.multiplier
        return Comparison(value)


class Negate(Compare):
    def __init__(self, honest: Union["Compare", list, tuple] | None = None):
        self.honest = Compare.load(honest)

    def __call__(self, 
        comparison: Comparison, 
        user: User, left: Entity, right: Entity, 
        left_public: bool, right_public, 
        criterion: str
    ) -> Comparison:
        return - self.honest(comparison, user, left, right, left_public, right_public, criterion)
        