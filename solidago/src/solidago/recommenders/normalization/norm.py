from numpy.typing import NDArray
import numpy as np

from .normalization import Normalization
from solidago.poll import *


class Norm(Normalization):
    def __init__(self, q: float):
        assert q >= 1
        self.q = q

    def norm(self, x: NDArray[np.float64]) -> float:
        if np.isinf(self.q):
            return x.max()
        return np.power(np.power(x, self.q).sum(), 1./self.q)

    def __call__(self, ballots: Scores) -> Scores:
        norm = self.norm(ballots.get_column("value").to_numpy(np.float64))
        normalized_ballots = ballots / Score(norm)
        assert isinstance(normalized_ballots, Scores)
        return normalized_ballots