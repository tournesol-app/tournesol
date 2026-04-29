from abc import abstractmethod
from solidago.poll import *

class Representative:
    def __init__(self, poll: Poll, user: User | str):
        self.poll = poll
        self.user = user if isinstance(user, User) else poll.users[user]

    @abstractmethod
    def __call__(self, target_user: User | None = None) -> Scores:
        raise NotImplemented
