from abc import abstractmethod

from solidago.poll import *

class SetWeights:
    @abstractmethod
    def __call__(self, poll: Poll, username: str, cursor: str | None = None) -> Entities:
        raise NotImplemented
