from solidago.poll import *
from solidago.modules import StateFunction


class VouchGen(StateFunction):
    def __call__(self, users: Users) -> Vouches:
        return Vouches()
