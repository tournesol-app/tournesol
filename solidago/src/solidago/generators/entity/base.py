import pandas as pd

from solidago.poll import *
from solidago.modules import PollFunction


class EntityGen(PollFunction):
    def __init__(self, n_entities: int=30):
        assert isinstance(n_entities, int) and n_entities > 0
        self.n_entities = n_entities
    
    def __call__(self) -> Entities:
        return Entities([ self.sample(f"entity_{e}") for e in range(self.n_entities) ])
    
    def sample(self, entity_name: str) -> Entities:
        return Entity(entity_name)
