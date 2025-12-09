from solidago.poll import *
from solidago.modules import PollFunction


class VouchGen(PollFunction):
    def __call__(self, users: Users) -> Vouches:
        return Vouches()
