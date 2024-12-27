from abc import ABC, abstractmethod

from solidago.pipeline.base import StateFunction
from solidago.state import State, Users, Vouches


class TrustPropagation(StateFunction):
    def __call__(self, state: State) -> None:
        state.users = self.propagate(state.users, state.vouches)
    
    @abstractmethod
    def propagate(self, users: Users, vouches: Vouches) -> Users:
        raise NotImplemented
    
    def __str__(self):
        return type(self).__name__
