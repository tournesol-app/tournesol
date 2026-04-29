from .normalization import Normalization

class Norm(Normalization):
    def __init__(self, q: float):
        assert q >= 1
        self.q = q