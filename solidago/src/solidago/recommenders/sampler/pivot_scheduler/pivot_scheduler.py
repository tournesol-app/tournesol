from abc import abstractmethod
import numpy as np
from solidago.poll import *

class PivotScheduler:
    @abstractmethod
    def __call__(self, entities: Entities) -> tuple[Entity, Entity]:
        raise NotImplemented
    
class Uniform:
    @abstractmethod
    def __call__(self, entities: Entities) -> tuple[Entity, Entity]:
        i, j = np.random.choice(len(entities), 2, False)
        e, f = entities[i], entities[j]
        assert isinstance(e, Entity) and isinstance(f, Entity)
        return e, f