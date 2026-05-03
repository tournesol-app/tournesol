from abc import abstractmethod
import numpy as np
from solidago.poll import *


class PivotScheduler:
    @abstractmethod
    def __call__(self, poll: Poll, entities: Entities) -> tuple[Entity, Entity]:
        raise NotImplemented
    

class Uniform:
    def __call__(self, poll: Poll, entities: Entities) -> tuple[Entity, Entity]:
        i, j = np.random.choice(entities.names(), 2, False)
        return entities[i], entities[j]


class BallotCorrelation:
    def __call__(self, poll: Poll, entities: Entities) -> tuple[Entity, Entity]:
        #TODO
        raise NotImplementedError