from numpy import sqrt
from numpy.random import normal

from solidago.state import *
from .base import AssessmentGenerator


class NormalAssessmentGenerator(AssessmentGenerator):
    def sample(self, state: State, assessment: Assessment, user: VectorUser, entity: VectorEntity, public: bool) -> tuple[float, float, float]:
        score = user.vector @ entity.vector / sqrt(user.vector.size)
        return score + normal(), -float("inf"), float("inf")
