from abc import abstractmethod
from typing import Any, Generic, Self, TypeVar


Object = TypeVar("Object")

class Similarity(Generic[Object]):
    @abstractmethod
    def __call__(self, object1: Object, object2: Object) -> float:
        """ Computes similarity between object1 and object2 """
