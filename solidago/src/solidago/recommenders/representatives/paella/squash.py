""" Useful squash functions to bound weights """
from numpy.typing import NDArray
import numpy as np


def squash(self, x: NDArray) -> NDArray:
    """ Must map [0, inf] to [0, 1] increasingly and bijectively """
    return np.where(x == np.inf, 1., x / (1. + x))

def shifted_squash(self, x: NDArray, max: float) -> NDArray:
    """ Must map [0, inf] to [1, max] increasingly and bijectively """
    return (max - 1.) * self.squash(x) + 1.

    def values(self, user: User, entities: Entities, poll: Poll) -> NDArray:
        values = np.array([self.shifted_squash(user["update_time"] / e["creation_date"], self.time_max) for e in entities])
        values *= self.shifted_squash(self.timeless_utility(user, poll), self.utility_max)
        sister_values = np.array([
            np.array([value for value, f in zip(values, entities) if self.entity_similarity(e, f) > 0])
            for e in entities
        ])
        values *= self.squash(self.source_max / sister_values)
        return values