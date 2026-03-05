from abc import ABC, abstractmethod
from solidago.state import State


class StateFunction(ABC):
    @abstractmethod
    def __call__(self, state: State) -> State:
        ...
