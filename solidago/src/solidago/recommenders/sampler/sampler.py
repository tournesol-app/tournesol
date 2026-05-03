from abc import abstractmethod

from solidago.poll import *


class Sampler:
    @abstractmethod
    def __call__(self, poll: Poll, limit: int) -> Entities:
        raise NotImplemented