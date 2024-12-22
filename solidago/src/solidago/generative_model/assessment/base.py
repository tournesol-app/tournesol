from abc import ABC, abstractmethod
from typing import Optional

import numpy as np

from solidago.state import Users, Entities, VotingRights, Assessments, Judgments


class AssessmentGenerator(ABC):
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        voting_rights: VotingRights, 
        judgments: Judgments
    ) -> Assessments:
        """ Fills in the comparisons """
        for index, assessment in judgments.assessments.iterrows():
            judgments.assessments.loc[index, "assessment_min"] = 0
            judgments.assessments.loc[index, "assessment_max"] = 1
            judgments.assessments.loc[index, "comparison"] = np.random.random()
        return judgments.assessments

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )
