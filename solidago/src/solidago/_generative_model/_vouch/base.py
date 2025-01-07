from solidago._state import *
from solidago._pipeline import StateFunction


class VouchGenerator(StateFunction):
    def __call__(self, users: Users) -> Vouches:
        return Vouches()
