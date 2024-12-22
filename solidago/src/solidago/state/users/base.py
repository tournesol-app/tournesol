from typing import Union

import pandas as pd


class User(pd.Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __hash__(self):
        return hash(self.name)


class Users(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "username" not in self.columns:
            assert len(self) == 0
            self["username"] = list()
        self.set_index("username", inplace=True)
        self.iterator = None

    @classmethod
    def load(cls, filename: str):
        return cls(pd.read_csv(filename, keep_default_na=False))

    def save(self, directory) -> Union[str, list, dict]:
        path = Path(directory) / "users.csv"
        self.to_csv(path)
        return str(path)
                
    def get(self, username):
        assert isinstance(username, User) or username in self.index, (username, self)
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
        return user.name in set(self["username"])

