from typing import Optional

import numpy as np

from solidago.state import *


class ComparisonGenerator:
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        criteria: Criteria,
        made_public: MadePublic, 
        comparisons: Comparisons
    ) -> Comparisons:
        """ Fills in the comparisons """
        for username, left_name, right_name, criterion_name in comparisons:
            user = users.get(username)
            criterion = criteria.get(criterion_name)
            left = entities.get(left_name)
            right = entities.get(right_name)
            left_public = made_public[user, left]
            right_public = made_public[user, right]
            comparison_max, comparison = self.sample(user, left, right, criterion, lpublic, rpublic)
            comparisons[user, criterion, left, right] |= {
                "comparison_max": comparison_max,
                "comparison": comparison
            }
        return comparisons
    
    def sample(self, 
        user: User, 
        left: Entity, 
        right: Entity, 
        criterion: Criterion, 
        left_public: bool, 
        right_public: bool
    ) -> tuple[float, float]:
        """ Returns comparison max and value """
        return 1, (2 * np.random.random() - 1)**2

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )
