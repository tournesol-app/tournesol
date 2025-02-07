from numpy import sqrt
from numpy.random import normal

from solidago.state import *
from .base import AssessmentGen


class NormalAssessment(AssessmentGen):
    def __init__(self, error_size: float=1):
        self.error_size = error_size

    def sample(self, 
        assessment: Assessment, 
        user: User, 
        entity: Entity, 
        public: bool, 
        criterion: str
    ) -> Assessment:
        score = user.vector @ entity.vector / sqrt(user.vector.size)
        if "is_trustworthy" in user and not user["is_trustworthy"]:
            score = - score
        else:
            score += self.error_size * normal()
        assessment["value"] = score
        assessment["min"] = -float("inf")
        assessment["max"] = float("inf")
        return assessment
