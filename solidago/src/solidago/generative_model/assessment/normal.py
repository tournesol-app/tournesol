from numpy import sqrt
from numpy.random import normal

from solidago.state import VectorUser, VectorEntity, VotingRights, Assessments, Judgments
from .base import AssessmentGenerator


class NormalAssessmentGenerator(AssessmentGenerator):
    def sample(self, user: VectorUser, entity: VectorEntity, private: bool) -> tuple[float, float, float]:
        score = user.vector @ entity.vector / sqrt(user.vector.size)
        return -float("inf"), float("inf"), score + normal()

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )
