from typing import Optional

import numpy as np

from solidago._state import *
from solidago._pipeline import StateFunction


class ComparisonGenerator(StateFunction):
    def __call__(self, users: Users, entities: Entities, made_public: MadePublic, comparisons: Comparisons) -> Comparisons:
        """ Fills in the comparisons """
        result = Comparisons()
        for (username, criterion, left_name, right_name), comparison in comparisons:
            comparison = self.sample(
                comparison=comparison,
                user=users.get(username), 
                left=entities.get(left_name), 
                right=entities.get(right_name),
                left_public=made_public[username, left_name],
                right_public=made_public[username, right_name], 
                criterion=criterion
            )
            result.add_row((username, criterion, left_name, right_name), comparison)
        return result
    
    def sample(self, 
        comparison: Comparison,
        user: User, 
        left: Entity, 
        right: Entity, 
        left_public: bool, 
        right_public: bool, 
        criterion: str
    ) -> Comparison:
        """ Returns comparison max and value """
        comparison["comparison"] = (2 * np.random.random() - 1)**2
        comparison["comparison_max"] = 1
        return comparison
