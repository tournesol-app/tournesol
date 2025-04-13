from typing import Optional

import numpy as np

from solidago.state import *
from solidago.modules import StateFunction


class ComparisonGen(StateFunction):
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        made_public: MadePublic, 
        comparisons: Comparisons
    ) -> Comparisons:
        """ Fills in the comparisons """
        result = Comparisons()
        for (username, criterion, left_name, right_name), comparison in comparisons:
            user, left, right = users[username], entities[left_name], entities[right_name]
            left_public, right_public = made_public[user, left], made_public[user, right]
            comparison = self.sample(comparison, user, left, right, left_public, right_public, criterion)
            result[username, criterion, left_name, right_name] = comparison
        return result
    
    def sample(self, comparison: Comparison, user: User, left: Entity, right: Entity, 
            left_public: bool, right_public: bool, criterion: str) -> Comparison:
        return Comparison((2 * np.random.random() - 1)**2, 1)
