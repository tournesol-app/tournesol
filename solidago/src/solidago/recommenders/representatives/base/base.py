from abc import abstractmethod
from solidago.poll import *

class BaseBallots:
    @abstractmethod
    def __call__(self, entities: Entities, ratings: Ratings) -> Scores:
        raise NotImplemented