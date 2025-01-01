import pandas as pd

from solidago.state import *
from solidago.pipeline import StateFunction


class EntityGenerator(StateFunction):
    entities_cls: type=Entities
    
    def __init__(self, n_entities: int=30):
        assert isinstance(n_entities, int) and n_entities > 0
        self.n_entities = n_entities
    
    def main(self) -> Entities:
        return self.entities_cls([ self.sample(e) for e in range(self.n_entities) ])
    
    def sample(self, entity_name: int) -> Entities:
        return self.entities_cls.series_cls(name=entity_name)
        
    def __str__(self):
        return type(self).__name__
    
    def to_json(self):
        return (type(self).__name__, )


