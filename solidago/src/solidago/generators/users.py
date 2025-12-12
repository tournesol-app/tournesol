import numpy as np

from solidago.generators.generator import GeneratorStep
from solidago.primitives.random import Distribution
from solidago import poll


class Users(GeneratorStep):
    def __init__(self, n_users: int = 30, distribution: Distribution | tuple | list | None = None):
        self.n_users = n_users
        if distribution:
            self.distribution = Distribution.load(distribution)
    
    def sample_user(self, user_index: int) -> poll.User:
        vector = self.distribution.sample() if hasattr(self, "distribution") else None
        return poll.User(f"user_{user_index}", vector)

    def __call__(self) -> poll.Users:
        return poll.Users([self.sample_user(user_index) for user_index in range(self.n_users)])

class AddColumn(GeneratorStep):
    def __init__(self, column: str, distribution: Distribution | tuple | list):
        self.column = column
        self.distribution = Distribution.load(distribution)
    
    def __call__(self, users: poll.Users) -> poll.Users:
        for user in users:
            user[self.column] = self.distribution.sample()[0]
        return users

class BernoulliPretrust(GeneratorStep):
    def __init__(self, p_if_trustworthy: float, p_if_untrustworthy: float=0.0):
        assert p_if_trustworthy >= 0 and p_if_trustworthy <= 1
        assert p_if_untrustworthy >= 0 and p_if_untrustworthy <= 1
        self.p_if_trustworthy = p_if_trustworthy
        self.p_if_untrustworthy = p_if_untrustworthy
    
    def __call__(self, users: poll.Users) -> poll.Users:
        def sample(is_trustworthy):
            return np.random.random() < (self.p_if_trustworthy if is_trustworthy else self.p_if_untrustworthy)
        values = [sample(user.is_trustworthy) for user in users]
        return users.assign(is_pretrusted=values)
