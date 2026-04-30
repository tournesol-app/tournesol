from abc import abstractmethod
from solidago.poll import *

class BallotBiasing:
    @abstractmethod
    def __call__(self, entities: Entities, ballot: Scores) -> Scores:
        raise NotImplemented
