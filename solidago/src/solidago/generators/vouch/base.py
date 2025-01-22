from solidago.state import *
from solidago.modules import StateFunction


class VouchGenerator(StateFunction):
    def __call__(self, users: Users) -> Vouches:
        return Vouches()
