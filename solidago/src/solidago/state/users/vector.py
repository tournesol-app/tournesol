from typing import Union, Optional
from types import SimpleNamespace

import pandas as pd
import numpy as np

from .base import User, Users


class VectorUser(User):
    def __init__(self, name: str, vector: np.ndarray, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = name
        self.vector = vector


class VectorUsers(Users):
    def __init__(self, users: list[VectorUser], vectors: Optional[np.ndarray]=None):
        super().__init__(users)
        self["vector_index"] = list(range(len(self)))
        self.meta = SimpleNamespace()
        self.meta.vectors = np.vstack([ user.vector for user in users ]) if vectors is None else vectors
        
    @property
    def vectors(self):
        return self.meta.vectors
    
    @vectors.setter
    def vectors(self, value):
        self.meta.vectors = value

    @classmethod
    def load(cls, filenames: tuple[str, str]):
        return cls(
            pd.read_csv(filenames[0], keep_default_na=False),
            vectors=np.loadtxt(filenames[1], delimiter=",")
        )

    def save(self, directory) -> Union[str, list, dict]:
        path = Path(directory)
        users_path, vectors_path = path / "users.csv", path / "users_vectors.csv"
        self.to_csv(users_path)
        np.savetxt(vectors_path, self.vectors, delimiter=",")
        return str(users_path), str(vectors_path)

    def get(self, user: Union[int, str, VectorUser]) -> VectorUser:
        username = user if isinstance(user, (int, str)) else user.name
        assert username in self.index, (username, self)
        user_row = self.loc[username]
        return VectorUser(username, self.vectors[user_row["vector_index"]], user_row)
        
    def __iter__(self):
        iterator = self.iterrows()
        while True:
            try: 
                username, row = next(iterator)
                yield VectorUser(username, self.vectors[row["vector_index"]], row)
            except StopIteration: break
        
    def __repr__(self) -> str:
        return repr(pd.DataFrame(self))
    
    def __contains__(self, user: Union[str, VectorUser]) -> bool:
        username = user if isinstance(username, str) else user.name
        return username in self["username"]

    def append(self, user: VectorUser) -> "VectorUsers":
        user["vector_index"] = len(self)
        self._append(user)
        self.vectors = np.vstack([self.vectors, user.vector])
        return self
    
    def delete(self, user: VectorUser) -> "VectorUsers":
        username = user if isinstance(username, str) else user.name
        user_index = self.loc[username, "vector_index"]
        self.vectors = np.delete(self.vectors, user_index, axis=0)
        self.drop(user_index)
        self["vector_index"] = list(range(len(self)))
        return self
