from typing import Union

import pandas as pd

from solidago.poll import *
from solidago.modules import PollFunction


class UserGen(PollFunction):
    output_key_names: list[str]=["users"]
    
    def __init__(self, n_users: int=30):
        assert isinstance(n_users, int) and n_users > 0
        self.n_users = n_users
    
    def __call__(self) -> Users:
        return Users([ self.sample(f"user_{u}") for u in range(self.n_users) ])
    
    def sample(self, username: str) -> User:
        return User(username)
