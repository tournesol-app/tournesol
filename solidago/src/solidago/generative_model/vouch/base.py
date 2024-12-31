from solidago.state import *
from solidago.pipeline import StateFunction


class VouchGenerator(StateFunction):
    def __call__(self, state: State) -> None:
        state.vouches = self.sample_vouches(state.users)
    
    def sample_vouches(self, users: Users) -> Vouches:
        return Vouches()
