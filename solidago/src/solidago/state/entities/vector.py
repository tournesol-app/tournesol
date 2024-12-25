from typing import Union, Optional
from types import SimpleNamespace
from pathlib import Path
from pandas import DataFrame

import pandas as pd
import numpy as np

from .base import Entity, Entities


class VectorEntity(Entity):
    def __init__(self, entity_id: str, vector: np.ndarray, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = str(entity_id)
        self.vector = vector
        

class VectorEntities(Entities):
    def __init__(self, entities: list[VectorEntity], vectors: Optional[np.ndarray]=None):
        super().__init__(entities)
        self["vector_index"] = list(range(len(self)))
        self.meta = SimpleNamespace()
        self.meta.vectors = np.vstack([ entity.vector for entity in entities ]) if vectors is None else vectors
        
    @property
    def vectors(self) -> np.ndarray:
        return self.meta.vectors
    
    @vectors.setter
    def vectors(self, value: np.ndarray) -> None:
        self.meta.vectors = value

    @classmethod
    def load(cls, filenames: tuple[str, str]) -> "VectorEntities":
        return cls(
            pd.read_csv(filenames[0], keep_default_na=False),
            vectors=np.loadtxt(filenames[1], delimiter=",")
        )

    def save(self, directory) -> tuple[str, tuple[str, str]]:
        path = Path(directory)
        entities_path, vectors_path = path / "entities.csv", path / "entities_vectors.csv"
        self.to_csv(entities_path)
        np.savetxt(vectors_path, self.vectors, delimiter=",")
        return type(self).__name__, [str(entities_path), str(vectors_path)]

    def get(self, entity: Union[str, VectorEntity]) -> VectorEntity:
        assert str(entity) in self.index, (entity, self)
        row = self.loc[str(entity)]
        return VectorEntity(str(entity), self.vectors[row["vector_index"]], row)
        
    def __iter__(self):
        iterator = self.iterrows()
        while True:
            try:
                entity_id, row = next(iterator)
                yield VectorEntity(entity_id, self.vectors[row["vector_index"]], row)
            except StopIteration: break
    
    def __repr__(self) -> str:
        return repr(DataFrame(self))

    def append(self, entity: VectorEntity) -> "VectorEntities":
        entity["vector_index"] = len(self)
        self._append(entity)
        self.vectors = np.array([user.vector]) if len(self.vectors) == 0 else np.vstack([self.vectors, user.vector])
        return self
    
    def delete(self, entity: VectorEntity) -> "VectorEntities":
        entity_index = self.loc[str(entity), "vector_index"]
        self.vectors = np.delete(self.vectors, entity_index, axis=0)
        self.drop(entity_index)
        self["vector_index"] = list(range(len(self)))
        return self
