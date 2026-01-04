import numpy as np

from solidago.poll import *
from .base import PreferenceLearning


class IsAssessment(PreferenceLearning):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def left_unc(self, assessment):
        if not np.isfinite(assessment.min):
            return 1
        return (assessment.value - assessment.min) / 2
    
    def right_unc(self, assessment):
        if not np.isfinite(assessment.max):
            return 1
        return (assessment.max - assessment.value) / 2

    def user_learn(self,
        user: User, # not used
        entities: Entities, # not used
        assessments: Assessments, # keynames == ["criterion", "entity_name"]
        comparisons: Comparisons, # not used
        base_model: ScoringModel, # not used
    ) -> ScoringModel:
        model = ScoringModel()
        for keys, assessment in assessments:
            kwargs = assessments.keys2kwargs(*keys)
            entity_name, criterion = kwargs["entity_name"], kwargs["criterion"]
            uncertainties = self.left_unc(assessment), self.right_unc(assessment)
            model[entity_name, criterion] = Score(assessment.value, *uncertainties)
        return model