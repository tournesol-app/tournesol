from dataclasses import dataclass, replace

from .users import Users
from .vouches import Vouches


@dataclass(frozen=True)
class State:
    users: Users
    vouches: Vouches

    @classmethod
    def empty(cls):
        return cls(users=Users.from_dict({}), vouches=Vouches.from_dict({}))

    def copy(self):
        return replace(self)

    def assign(self, **kwargs):
        return replace(self, **kwargs)
