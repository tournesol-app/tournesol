from abc import abstractmethod
from solidago.poll import *

class BaseBallotConstructor:
    @abstractmethod
    def __call__(self, councillor: User, entities: Entities, ratings: Ratings) -> Scores:
        raise NotImplemented