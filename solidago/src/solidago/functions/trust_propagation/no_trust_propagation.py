from solidago.poll import *
from solidago.functions.poll_function import PollFunction


class NoTrustPropagation(PollFunction):
    def __init__(self, 
        pretrust_value: float = 0.8,
        default_pretrust: bool = True, 
        max_workers: int | None = None
    ):
        """
        Parameters
        ----------
        pretrust_value:
            trust score to assign to pretrusted users
        """
        super().__init__(max_workers)
        self.pretrust_value = pretrust_value
        self.default_pretrust = default_pretrust

    def fn(self, users: Users) -> Users:
        trusts = users("pretrust", self.default_pretrust) * self.pretrust_value
        return users.assign(trust=trusts)
