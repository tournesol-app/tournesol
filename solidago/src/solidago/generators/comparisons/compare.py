from abc import abstractmethod
from typing import Any, Union

import numpy as np

from solidago.poll import *


class Compare:
    @abstractmethod
    def __call__(self, 
        comparison: Comparison, 
        user: User, left: Entity, right: Entity, 
        left_public: bool, right_public: bool, 
        criterion: str,
    ) -> dict[str, Any]:
        raise NotImplemented
    
    def __repr__(self):
        t = ".".join(str(type(self)).split(".")[2:])[:-2]
        kwargs = ", ".join([f"{k}={v}" for k, v in self.__dict__.items()])
        return f"{t}({kwargs})"


class Deterministic(Compare):
    def __call__(self, 
        comparison: Comparison, 
        user: User, left: Entity, right: Entity, 
        left_public: bool, right_public: bool, 
        criterion: str,
    ) -> dict[str, Any]:
        value = user.vector @ (right.vector - left.vector) / np.sqrt(user.vector.size)
        if "multiplier" in user:
            value *= user["multiplier"]
        return dict(value=value, max=float("inf"))
    

class Negate(Compare):
    def __init__(self, honest: Union["Compare", list, tuple]):
        import solidago
        self.honest = solidago.load(honest, solidago.generators.comparisons, Compare)

    def __call__(self, 
        comparison: Comparison, 
        user: User, left: Entity, right: Entity, 
        left_public: bool, right_public: bool, 
        criterion: str,
    ) -> dict[str, Any]:
        kwargs = self.honest(comparison, user, left, right, left_public, right_public, criterion)
        kwargs["value"] = - kwargs["value"]
        return kwargs
        