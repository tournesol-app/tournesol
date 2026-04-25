from abc import abstractmethod
from numpy.typing import NDArray
import numpy as np

from solidago.poll import *
from .veche import Veche


class FairChronological(Veche):
    def __init__(self, 
        utility_max: float, 
        time_max: float, 
        source_max: float, 
        main_criterion: str
    ):
        self.utility_max = utility_max
        self.time_max = time_max
        self.source_max = source_max
        self.main_criterion = main_criterion

    @abstractmethod
    def __call__(self, poll: Poll, username: str, limit: int, cursor: str | None = None) -> Entities:
        """ Given a poll, computes a list of entities to be recommended """
    
    def timeless_utility(self, user: User, poll: Poll) -> NDArray:
        """ TBD """
        return np.array([poll.user_models[user](e, self.main_criterion) for e in poll.entities])

