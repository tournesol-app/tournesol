from typing import Optional

import numpy as np

from solidago.state import *


class ComparisonGenerator:
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        privacy: Privacy, 
        judgments: Judgments
    ) -> Comparisons:
        """ Fills in the comparisons """
        for index, comparison in judgments.comparisons.iterrows():
            user = users.get(comparison["username"])
            left = entities.get(comparison["left_id"])
            right = entities.get(comparison["right_id"])
            left_private = privacy[user, left]
            right_private = privacy[user, right]
            comparison_max, comparison = self.sample(user, left, right, left_private, right_private)
            judgments.comparisons.loc[index, "comparison_max"] = comparison_max
            judgments.comparisons.loc[index, "comparison"] = comparison
        return judgments.comparisons
    
    def sample(self, user: User, left: Entity, right: Entity, left_private: bool, right_private: bool) -> tuple[float, float]:
        """ Returns comparison max and value """
        return 1, (2 * np.random.random() - 1)**2

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )
