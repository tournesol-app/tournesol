import pandas as pd

from solidago.state import Entities


class EntityGenerator:
    def __call__(self, n_entities: int) -> Entities:
        return Entities([ self.sample(entity_id) for entity_id in range(n_entities) ])
    
    def sample(self, entity_id):
        return Entity(name=entity_id)
        
    def __str__(self):
        return type(self).__name__
    
    def to_json(self):
        return (type(self).__name__, )


