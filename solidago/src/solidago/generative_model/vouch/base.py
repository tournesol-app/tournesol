from solidago.state import *
from solidago.pipeline import StateFunction


class VouchGenerator(StateFunction):
    def main(self, users: Users) -> Vouches:
        return Vouches()
