from abc import abstractmethod
from solidago.poll import *


class Normalization:
    @abstractmethod
    def __call__(self, ballots: Scores) -> Scores:
        raise NotImplemented