from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


class NoTrustPropagation(PollFunction):
    def __init__(self, pretrust_value: float=0.8, *args, **kwargs):
        """
        Parameters
        ----------
        pretrust_value:
            trust score to assign to pretrusted users
        """
        super().__init__(*args, **kwargs)
        self.pretrust_value = pretrust_value

    def fn(self, users: Users, vouches: Vouches) -> Users:
        return users.assign(trust=(users.get_column("is_pretrusted") * self.pretrust_value))
