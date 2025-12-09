from solidago.poll import *
from solidago.modules.base import PollFunction


class TrustAll(PollFunction):
    """`TrustAll` is a naive solution that assignes an equal amount of trust to all users"""
    def __call__(self, users: Users, vouches: Vouches) -> Users:
        return users.assign(trust=1.0)
