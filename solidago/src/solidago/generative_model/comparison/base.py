from abc import ABC, abstractmethod
from typing import Optional

import numpy as np

from solidago.state import Users, Entities, VotingRights, Comparisons, Judgments


class ComparisonGenerator(ABC):
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        voting_rights: VotingRights, 
        judgments: Judgments
    ) -> Comparisons:
        """ Fills in the comparisons """
        for index, comparison in judgments.comparisons.iterrows():
            judgments.comparisons.loc[index, "comparison_max"] = 1
            judgments.comparisons.loc[index, "comparison"] = (2 * np.random.random() - 1)**2
        return judgments.comparisons

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )
