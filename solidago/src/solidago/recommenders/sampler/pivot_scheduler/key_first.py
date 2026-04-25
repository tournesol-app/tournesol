from solidago.poll import *
import numpy as np
from .pivot_scheduler import PivotScheduler, Uniform

class KeyFirst(PivotScheduler):
    def __init__(self, key: str, next: PivotScheduler | None):
        """ This scheduler first makes sure that each key is assigned to  """
        self.key = key
        self.next = Uniform() if next is None else next

    def __call__(self, entities: Entities) -> tuple[Entity, Entity]:
        values = entities.df.value_counts(self.key)
        if values.max() == 1:
            return self.next(entities)
        values = values[values == values.max()]
        value = values.index[np.random.randint(len(values))]
        subdf = entities.df[entities.df[self.key] == value]
        return Uniform()(Entities(subdf))
