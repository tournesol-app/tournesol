from typing import Union

import pandas as pd


class User(pd.Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @property
    def name(self):
        return self["username"]

    def __hash__(self):
        return int(self.name)


class Users(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.index.name = "username"
        self.iterator = None

    @classmethod
    def load(cls, filename: str):
        return cls(pd.read_csv(filename, keep_default_na=False))

    def save(self, directory) -> Union[str, list, dict]:
        path = Path(directory) / "users.csv"
        self.to_csv(path)
        return str(path)
                
    def get(self, username):
        return username if isinstance(username, User) else User(self.loc[username])
        
    def __iter__(self):
        self.iterator = super(Users, self).iterrows()
        return self
    
    def __next__(self):
        _, user = next(self.iterator)
        return User(user)
    
    def __repr__(self):
        return repr(pd.DataFrame(self))
    
    def __contains__(self, user: User):
        return user.id in set(self["username"])

