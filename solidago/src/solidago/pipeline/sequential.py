from solidago.state import State
from .base import StateFunction


class Sequential(StateFunction):
    def __init__(self, *modules):
        for module in modules:
            assert isinstance(module, StateFunction)
        self.modules = modules
    
    def __call__(self, state: State) -> State:
        for module in self.modules:
            state = self.module(state)
        return state

