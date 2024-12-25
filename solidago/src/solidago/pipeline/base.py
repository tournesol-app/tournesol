from abc import ABC, abstractmethod

from solidago.state import State


class StateFunction(ABC):
    @abstractmethod
    def __call__(self, state: State) -> State:
        raise NotImplemented

    def to_json(self):
        return (type(self).__name__, dict())
    
    def __str__(self):
        return type(self).__name__
