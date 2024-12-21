from typing import Union

import pandas as pd


class Entity(pd.Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def id(self):
        return self["entity_id"]
    
    def __hash__(self):
        return int(self.id)
        

class Entities(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index.name = "entity_id"
        self.iterator = None

    @classmethod
    def load(cls, filename: str):
        return cls(pd.read_csv(filename, keep_default_na=False))

    def save(self, directory) -> Union[str, list, dict]:
        path = Path(directory) / "entities.csv"
        self.to_csv(path)
        return str(path)

    def get(self, entity_id):
        return entity_id if isinstance(entity_id, Entity) else Entity(self.loc[entity_id])
        
    def __iter__(self):
        self.iterator = super(Entities, self).iterrows()
        return self
    
    def __next__(self):
        _, entity = next(self.iterator)
        return Entity(entity)
    
    def __repr__(self):
        return repr(pd.DataFrame(self))
    
    def __contains__(self, entity: Entity):
        return entity.id in set(self["entity_id"])

