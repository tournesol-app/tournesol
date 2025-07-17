from dataclasses import dataclass, replace

from .users import Users
from .vouches import Vouches


@dataclass(frozen=True)
class State:
    users: Users
    vouches: Vouches

    def copy(self):
        return replace(self)
