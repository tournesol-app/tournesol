from abc import abstractmethod
from typing import Any, Generic, Self, TypeVar


_LoadableType = type | str | tuple[str | type, dict[str, Any]] | list[str | type | dict[str, Any]] | dict[str, Any]

Object = TypeVar("Object")

class Similarity(Generic[Object]):
    @abstractmethod
    def __call__(self, object1: Object, object2: Object) -> float:
        """ Computes similarity between object1 and object2 """
    
    @classmethod
    def load(cls, arg: _LoadableType | Self | None = None, **kwargs: Any) -> "Similarity":
        if isinstance(arg, Similarity):
            return arg
        import solidago
        s = solidago.load(arg or dict(), solidago.primitives.minimizer, **kwargs)
        assert isinstance(s, Similarity)
        return s
    