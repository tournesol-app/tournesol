from solidago.poll import *
from .representative import Representative
from .base import Direct
from ..bias import QuadraticTimeDecay

class ChronoRepresentative(Representative):
    def __init__(self, poll: Poll, councillor: User | str):
        super().__init__(poll, councillor, Direct(self.councillor), [QuadraticTimeDecay()])