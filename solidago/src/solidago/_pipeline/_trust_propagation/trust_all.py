from solidago._state import *
from solidago._pipeline.base import StateFunction


class TrustAll(StateFunction):
    """`TrustAll` is a naive solution that assignes an equal amount of trust to all users"""
    def __call__(self, users: Users, vouches: Vouches) -> Users:
        users["trust_score"] = 1.
        return users
