from typing import Union

import pandas as pd

from solidago.state import *
from solidago.pipeline import StateFunction


class UserGenerator(StateFunction):
    output_key_names: list[str]=["users"]
    users_cls: type=Users
    
    def __init__(self, n_users: int=30):
        assert isinstance(n_users, int) and n_users > 0
        self.n_users = n_users
    
    def main(self, users: Users, vouches: Vouches) -> Users:
        return self.users_cls([ self.sample(username) for username in range(self.n_users) ])
    
    def sample(self, username: Union[int, str]) -> User:
        return self.users_cls.series_cls(name=username)
