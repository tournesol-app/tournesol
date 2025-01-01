from typing import Optional

import numpy as np

from solidago.state import *
from solidago.pipeline import StateFunction


class ComparisonGenerator(StateFunction):
    def __call__(self, state: State) -> None:
        """ Fills in the comparisons """
        comparisons = Comparisons()
        for (username, left_name, right_name), comparisons_list in state.comparisons:
            comparisons[username, left_name, right_name] = list()
            for index, comparison in enumerate(comparisons_list):
                user = state.users.get(username)
                left = state.entities.get(left_name)
                right = state.entities.get(right_name)
                left_public = state.made_public[user, left]
                right_public = state.made_public[user, right]
                comparison_value, comparison_max = self.sample(user, left, right, left_public, right_public)
                if "is_trustworthy" in user and not user["is_trustworthy"]:
                    comparison_value = - comparison_value
                comparisons[user, left, right].append(dict(comparison) | {
                    "comparison_max": comparison_max,
                    "comparison": comparison_value
                })
        return comparisons
    
    def sample(self, user: User, left: Entity, right: Entity, left_public: bool, right_public: bool) -> tuple[float, float]:
        """ Returns comparison max and value """
        return (2 * np.random.random() - 1)**2, 1
