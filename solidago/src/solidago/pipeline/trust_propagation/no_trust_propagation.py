from .base import TrustPropagation
from solidago.state import Users, Vouches


class NoTrustPropagation(TrustPropagation):
    def __init__(self, pretrust_value: float=0.8,):
        """
        Parameters
        ----------
        pretrust_value:
            trust score to assign to pretrusted users
        """
        self.pretrust_value = pretrust_value

    def main(self, users: Users, vouches: Vouches) -> Users:
        users["trust_score"] = users["is_pretrusted"] * self.pretrust_value
        return users
