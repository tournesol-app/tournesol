from abc import ABC, abstractmethod
from solidago.poll import Poll


class PollFunction(ABC):
    @abstractmethod
    def __call__(self, poll: Poll) -> Poll:
        ...
