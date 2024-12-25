from typing import Union, Optional
from types import SimpleNamespace
from pathlib import Path
from pandas import DataFrame

import pandas as pd
import numpy as np

from .base import User, Users


class VectorUser(User):
    def __init__(self, name: str, vector: np.ndarray, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = str(name)
        self.vector = vector


class VectorUsers(Users):
    def __init__(self, users: list[VectorUser], vectors: Optional[np.ndarray]=None):
        super().__init__(users)
        self["vector_index"] = list(range(len(self)))
        self.meta = SimpleNamespace()
        self.meta.vectors = np.vstack([ user.vector for user in users ]) if vectors is None else vectors
        
    @property
    def vectors(self) -> np.ndarray:
        return self.meta.vectors
    
    @vectors.setter
    def vectors(self, value) -> None:
        self.meta.vectors = value

    @classmethod
    def load(cls, filenames: tuple[str, str]) -> "VectorUsers":
        return cls(
            pd.read_csv(filenames[0], keep_default_na=False),
            vectors=np.loadtxt(filenames[1], delimiter=",")
        )

    def save(self, directory) -> tuple[str, [str, str]]:
        path = Path(directory)
        users_path, vectors_path = path / "users.csv", path / "users_vectors.csv"
        self.to_csv(users_path)
        np.savetxt(vectors_path, self.vectors, delimiter=",")
        return type(self).__name__, [str(users_path), str(vectors_path)]

    def get(self, user: Union[str, VectorUser]) -> VectorUser:
        assert str(user) in self.index, (user, self)
        row = self.loc[str(user)]
        return VectorUser(str(user), self.vectors[row["vector_index"]], row)
        
    def __iter__(self):
        iterator = self.iterrows()
        while True:
            try: 
                username, row = next(iterator)
                yield VectorUser(username, self.vectors[row["vector_index"]], row)
            except StopIteration: break
        
    def __repr__(self) -> str:
        return repr(DataFrame(self))

    def append(self, user: VectorUser) -> "VectorUsers":
        user["vector_index"] = len(self)
        self._append(user)
        self.vectors = np.vstack([self.vectors, user.vector])
        return self
    
    def delete(self, user: VectorUser) -> "VectorUsers":
        user_index = self.loc[str(user), "vector_index"]
        self.vectors = np.delete(self.vectors, user_index, axis=0)
        self.drop(user_index)
        self["vector_index"] = list(range(len(self)))
        return self
