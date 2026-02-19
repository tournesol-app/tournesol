from typing import Any
import numpy as np

from solidago.poll_functions.poll_function import PollFunction
from solidago.primitives.random import Distribution
from solidago import poll


class New(PollFunction):
    def __init__(self, n_users: int = 30, distribution: Distribution | tuple[str, dict[str, Any]] | None = None):
        self.n_users = n_users
        if distribution:
            import solidago
            distribution = solidago.load(distribution, solidago.random)
            assert isinstance(distribution, Distribution)
            self.distribution = distribution
    
    def sample_user(self, user_index: int) -> poll.User:
        vector = self.distribution.sample() if hasattr(self, "distribution") else None
        return poll.User(f"user_{user_index}", vector=vector)

    def __call__(self) -> poll.Users:
        return poll.Users([self.sample_user(user_index).series for user_index in range(self.n_users)])

class AddColumn(PollFunction):
    def __init__(self, column: str, distribution: Distribution | tuple[str, dict[str, Any]]):
        self.column = column
        import solidago
        distribution = solidago.load(distribution, solidago.random)
        assert isinstance(distribution, Distribution)
        self.distribution = distribution
    
    def __call__(self, users: poll.Users) -> poll.Users:
        return users.assign(**{self.column: self.distribution.sample(len(users))})

class BernoulliPretrust(PollFunction):
    def __init__(self, p_if_trustworthy: float, p_if_untrustworthy: float=0.0):
        assert p_if_trustworthy >= 0 and p_if_trustworthy <= 1
        assert p_if_untrustworthy >= 0 and p_if_untrustworthy <= 1
        self.p_if_trustworthy = p_if_trustworthy
        self.p_if_untrustworthy = p_if_untrustworthy
    
    def __call__(self, users: poll.Users) -> poll.Users:
        is_trustworthy = users.get_column("is_trustworthy")
        pretrust = np.random.random(len(users)) < np.where(is_trustworthy, self.p_if_trustworthy, self.p_if_untrustworthy)
        return users.assign(pretrust=pretrust)
