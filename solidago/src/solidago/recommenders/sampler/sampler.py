from abc import abstractmethod

from solidago.poll import *


class Sampler:
    def __init__(self, criterion: str = "main"):
        self.criterion = criterion
        
    @abstractmethod
    def __call__(self, poll: Poll, limit: int) -> Entities:
        raise NotImplemented