from typing import Union

import pandas as pd


class Entity(pd.Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def id(self):
        return self.name
    
    @id.setter
    def id(self, entity_id):
        self.name = entity_id
    
    def __hash__(self):
        return hash(self.id)
        

class Entities(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.columns:
            self.set_index("entity_id", inplace=True)
        else:
            self.index.name = "entity_id"
        self.iterator = None

    @classmethod
    def load(cls, filename: str):
        return cls(pd.read_csv(filename, keep_default_na=False))

    def save(self, directory) -> Union[str, list, dict]:
        path = Path(directory) / "entities.csv"
        self.to_csv(path)
        return str(path)

    def get(self, entity_id: Union[str, int, Entity]) -> Entity:
        assert isinstance(entity_id, Entity) or entity_id in self.index, (entity_id, self)
        return entity_id if isinstance(entity_id, Entity) else Entity(self.loc[entity_id])
        
    def __iter__(self):
        iterator = self.iterrows()
        while True:
            try: yield Entity(next(iterator)[1])
            except StopIteration: break
    
    def __repr__(self):
        return repr(pd.DataFrame(self))
    
    def __contains__(self, entity: Entity):
        return entity.id in set(self["entity_id"])

