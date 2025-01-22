from solidago.state import *
from solidago.modules.base import StateFunction


class NoTrustPropagation(StateFunction):
    def __init__(self, pretrust_value: float=0.8,):
        """
        Parameters
        ----------
        pretrust_value:
            trust score to assign to pretrusted users
        """
        self.pretrust_value = pretrust_value

    def __call__(self, users: Users, vouches: Vouches) -> Users:
        return users.assign(trust_score=(users["is_pretrusted"] * self.pretrust_value))
