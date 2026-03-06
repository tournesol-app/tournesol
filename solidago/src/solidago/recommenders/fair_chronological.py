from abc import abstractmethod
from numpy.typing import NDArray
import numpy as np

from solidago.poll import *
from solidago.primitives.similarity import Similarity


class FairChronological:
    def __init__(self, 
        utility_max: float, 
        time_max: float, 
        source_max: float, 
        entity_similarity: Similarity, 
        main_criterion: str
    ):
        self.utility_max = utility_max
        self.time_max = time_max
        self.source_max = source_max
        self.entity_similarity = entity_similarity
        self.main_criterion = main_criterion

    @abstractmethod
    def __call__(self, poll: Poll, username: str, limit: int, cursor: str | None = None) -> Entities:
        """ Given a poll, computes a list of entities to be recommended """

    def squash(self, x: NDArray) -> NDArray:
        """ Must map [0, inf] to [0, 1] increasingly and bijectively """
        return np.where(x == np.inf, 1., x / (1. + x))
    
    def shifted_squash(self, x: NDArray, max: float) -> NDArray:
        """ Must map [0, inf] to [1, max] increasingly and bijectively """
        return (max - 1.) * self.squash(x) + 1.
    
    def timeless_utility(self, user: User, poll: Poll) -> NDArray:
        """ TBD """
        return np.array([poll.user_models[user](e, self.main_criterion) for e in poll.entities])

    def values(self, user: User, entities: Entities, poll: Poll) -> NDArray:
        values = np.array([self.shifted_squash(user["update_time"] / e["creation_date"], self.time_max) for e in entities])
        values *= self.shifted_squash(self.timeless_utility(user, poll), self.utility_max)
        sister_values = np.array([
            np.array([value for value, f in zip(values, entities) if self.entity_similarity(e, f) > 0])
            for e in entities
        ])
        values *= self.squash(self.source_max / sister_values)
        return values