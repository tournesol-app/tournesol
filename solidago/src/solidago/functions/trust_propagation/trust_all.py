from solidago.poll import *
from solidago.functions.poll_function import PollFunction


class TrustAll(PollFunction):
    """`TrustAll` is a naive solution that assignes an equal amount of trust to all users"""
    def fn(self, users: Users) -> Users:
        return users.assign(trust=1.0)
