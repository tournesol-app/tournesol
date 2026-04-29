from typing import Any
import numpy as np

from solidago.poll_functions.poll_function import PollFunction
from solidago.primitives.random import Distribution
from solidago import poll


class New(PollFunction):
    def __init__(self, 
        n_users: int = 30, 
        distribution: Distribution | tuple[str, dict[str, Any]] | None = None
    ):
        self.n_users = n_users
        import solidago
        self.distribution = None if distribution is None else solidago.load(
            distribution, solidago.random, Distribution)
    
    def sample_user(self, user_index: int) -> poll.User:
        if self.distribution is None:
            return poll.User(f"user_{user_index}")
        return poll.User(f"user_{user_index}", vector=self.distribution.sample())

    def fn(self) -> poll.Users:
        return poll.Users([self.sample_user(user_index).series for user_index in range(self.n_users)])

class AddColumn(PollFunction):
    def __init__(self, column: str, distribution: Distribution | tuple[str, dict[str, Any]]):
        self.column = column
        import solidago
        self.distribution = solidago.load(distribution, solidago.random, Distribution)
    
    def fn(self, users: poll.Users) -> poll.Users:
        return users.assign(**{self.column: self.distribution.sample(len(users))})

class BernoulliPretrust(PollFunction):
    def __init__(self, p_if_trustworthy: float, p_if_untrustworthy: float=0.0):
        assert p_if_trustworthy >= 0 and p_if_trustworthy <= 1
        assert p_if_untrustworthy >= 0 and p_if_untrustworthy <= 1
        self.p_if_trustworthy = p_if_trustworthy
        self.p_if_untrustworthy = p_if_untrustworthy
    
    def fn(self, users: poll.Users) -> poll.Users:
        trustworthy = users.get_column("trustworthy")
        args = self.p_if_trustworthy, self.p_if_untrustworthy
        pretrust = np.random.random(len(users)) < np.where(trustworthy, *args)
        return users.assign(pretrust=pretrust)
