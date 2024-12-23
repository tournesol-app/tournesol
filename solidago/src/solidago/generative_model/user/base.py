import pandas as pd

from solidago.state import User, Users


class UserGenerator:
    def __call__(self, n_users: int) -> Users:
        return Users([ self.sample(username) for username in range(n_users) ])
    
    def sample(self, username):
        return User(name=username)
    
    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )

