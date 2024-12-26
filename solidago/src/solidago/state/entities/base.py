from typing import Union
from pandas import Series, DataFrame
from pathlib import Path

import pandas as pd


class Entity(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = str(self.name)

    @property
    def id(self) -> str:
        return self.name
    
    @id.setter
    def id(self, entity_id) -> None:
        self.name = str(entity_id)
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __str__(self) -> str:
        return self.id
        

class Entities(DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self.columns) == 1:
            self.rename(columns={ self.columns[0]: "entity_id" }, inplace=True)
        if "entity_id" in self.columns:
            self.set_index("entity_id", inplace=True)
        self.index = [str(name) for name in self.index]
        self.index.name = "entity_id"

    @classmethod
    def load(cls, filename: str) -> "Entities":
        return cls(pd.read_csv(filename, keep_default_na=False))

    def save(self, directory) -> Union[str, list, dict]:
        path = Path(directory) / "entities.csv"
        self.to_csv(path)
        return type(self).__name__, str(path)

    def get(self, entity: Union[int, Entity]) -> Entity:
        assert str(entity) in self.index, (entity, self)
        return Entity(self.loc[str(entity)])
        
    def __iter__(self):
        iterator = self.iterrows()
        while True:
            try: yield Entity(next(iterator)[1])
            except StopIteration: break
    
    def __repr__(self) -> str:
        return repr(DataFrame(self))
    
    def __contains__(self, entity: Entity) -> str:
        return str(entity) in set(self.index)

