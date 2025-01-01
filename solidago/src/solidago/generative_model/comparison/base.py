from typing import Optional

import numpy as np

from solidago.state import *
from solidago.pipeline import StateFunction


class ComparisonGenerator(StateFunction):
    def main(self, users: Users, entities: Entities, made_public: MadePublic, comparisons: Comparisons) -> Comparisons:
        """ Fills in the comparisons """
        filled_comparisons = Comparisons()
        for (username, left_name, right_name), comparisons_list in comparisons:
            filled_comparisons[username, left_name, right_name] = list()
            for index, comparison in enumerate(comparisons_list):
                user = users.get(username)
                left = entities.get(left_name)
                right = entities.get(right_name)
                left_public = made_public[user, left]
                right_public = made_public[user, right]
                comparison_value, comparison_max = self.sample(user, left, right, left_public, right_public)
                filled_comparisons.add_row((user, left, right), dict(comparison) | {
                    "comparison_max": comparison_max,
                    "comparison": comparison_value
                })
        return filled_comparisons
    
    def sample(self, user: User, left: Entity, right: Entity, left_public: bool, right_public: bool) -> tuple[float, float]:
        """ Returns comparison max and value """
        return (2 * np.random.random() - 1)**2, 1
