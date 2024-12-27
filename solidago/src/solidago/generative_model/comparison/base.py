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
        for username, criterion_id, user_comparisons in comparisons:
            for index, comparison in user_comparisons.iterrows():
                user = users.get(username)
                left = entities.get(comparison["left_id"])
                right = entities.get(comparison["right_id"])
                comparison_max, comparison = self.sample(
                    user=user, left=left, right=right,
                    criterion=criteria.get(criterion_id), 
                    left_public=made_public[user, left], 
                    right_public=made_public[user, right]
                )
                user_comparisons.loc[index, "comparison_max"] = comparison_max
                user_comparisons.loc[index, "comparison"] = comparison
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
