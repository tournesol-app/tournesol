from abc import ABC, abstractmethod

from solidago.pipeline.base import StateFunction
from solidago.state import State, Users, Vouches


class TrustPropagation(StateFunction):
    @abstractmethod
    def main(self, users: Users, vouches: Vouches) -> Users:
        """ Propagates user trust through vouches, and stores result in state.users """
        return self.propagate(state.users, state.vouches)
    
