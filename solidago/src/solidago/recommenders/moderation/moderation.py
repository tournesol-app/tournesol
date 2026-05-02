from abc import abstractmethod
from solidago.poll import *


class Moderation:
    @abstractmethod
    def __call__(self, poll: Poll, receiver: User, time: int) -> Poll:
        raise NotImplemented