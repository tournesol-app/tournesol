from abc import abstractmethod
from solidago.poll import *


class Aggregator:
    @abstractmethod
    def __call__(self, poll: Poll, councillors: Users, ballots: Scores) -> Entities:
        raise NotImplemented