from numpy import sqrt
from numpy.random import normal

from solidago._state import *
from .base import AssessmentGenerator


class NormalAssessmentGenerator(AssessmentGenerator):
    def __init__(self, error_size: float=1):
        self.error_size = error_size
    
    def sample(self, 
        assessment: Assessment, 
        user: VectorUser, 
        entity: VectorEntity, 
        public: bool, 
        criterion: str
    ) -> tuple[float, float, float]:
        score = user.vector @ entity.vector / sqrt(user.vector.size)
        if "is_trustworthy" in user and not user["is_trustworthy"]:
            score = - score
        else:
            score += self.error_size * normal()
        return score, -float("inf"), float("inf")
