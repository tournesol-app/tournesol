from abc import abstractmethod
from solidago.poll import *

class BaseBallotConstructor:
    @abstractmethod
    def __call__(self, entities: Entities, ratings: Ratings) -> Scores:
        raise NotImplemented