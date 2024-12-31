import pandas as pd

from solidago.state import *
from solidago.pipeline import StateFunction


class UserGenerator(StateFunction):
    users_cls: type=Users
    
    def __init__(self, n_users: int=30):
        assert isinstance(n_users, int) and n_users > 0
        self.n_users = n_users
    
    def __call__(self, state: State) -> None:
        state.users = self.users_cls([ self.sample(username) for username in range(self.n_users) ])
    
    def sample(self, username: int):
        return self.users_cls.series_cls(name=username)
