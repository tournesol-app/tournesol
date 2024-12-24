from typing import Union
from pandas import DataFrame, Series
from pathlib import Path

import pandas as pd


class User(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __hash__(self):
        return hash(self.name)


class Users(DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" in self.columns:
            self.set_index("username", inplace=True)
        else:
            self.index.name = "username"

    @classmethod
    def load(cls, filename: str):
        return cls(pd.read_csv(filename, keep_default_na=False))

    def save(self, directory) -> Union[str, list, dict]:
        path = Path(directory) / "users.csv"
        self.to_csv(path)
        return type(self).__name__, str(path)
                
    def get(self, username: Union[int, str, User]) -> User:
        assert isinstance(username, User) or username in self.index, (username, self)
        return username if isinstance(username, User) else User(self.loc[username])
        
    def __iter__(self):
        iterator = self.iterrows()
        while True:
            try: yield User(next(iterator)[1])
            except StopIteration: break
    
    def __repr__(self):
        return repr(DataFrame(self))
    
    def __contains__(self, user: User):
        return user.name in set(self["username"])

