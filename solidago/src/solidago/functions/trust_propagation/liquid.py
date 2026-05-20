from typing import Iterable

from solidago.functions.poll_function import PollFunction
from solidago.primitives.decay import Decay
from solidago.poll import *


class Liquid(PollFunction):
    default_social_kinds: set[str] = {"relay"}

    def __init__(self, social_kinds: Iterable[str] | None = None):
        self.social_kinds = self.default_social_kinds if social_kinds is None else set(social_kinds)

    def fn(self, users: Users, socials: Socials) -> Users:
        users = users.assign(positive_volume=users("volume", 0) > 0)
        delegate_names = socials.filters(by=users.names(), kind=self.social_kinds).keys("to")
        delegates = [u.name in delegate_names for u in users]
        return users.assign(delegate=delegates, included=delegates | users("positive_volume"))