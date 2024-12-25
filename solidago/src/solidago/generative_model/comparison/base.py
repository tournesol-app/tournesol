from typing import Optional

import numpy as np

from solidago.state import *


class ComparisonGenerator:
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        criteria: Criteria,
        made_public: MadePublic, 
        judgments: Judgments
    ) -> Comparisons:
        """ Fills in the comparisons """
        for username, criterion_id, comparisons in judgments.comparisons:
            for index, comparison in comparisons.iterrows():
                comparison_max, comparison = self.sample(
                    user=users.get(comparison["username"]), 
                    left=entities.get(comparison["left_id"]), 
                    right=entities.get(comparison["right_id"]), 
                    criterion=criteria.get(criterion_id), 
                    left_public=made_public[user, left], 
                    rright_public=made_public[user, right]
                )
                judgments.comparisons.loc[index, "comparison_max"] = comparison_max
                judgments.comparisons.loc[index, "comparison"] = comparison
        return judgments.comparisons
    
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
