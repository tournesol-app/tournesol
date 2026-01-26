import numpy as np

from solidago.poll import *
from .preference_learning import PreferenceLearning


class IsRating(PreferenceLearning):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def left_unc(self, rating: Rating):
        if not np.isfinite(rating.min):
            return 1
        return (rating.value - rating.min) / 2
    
    def right_unc(self, rating: Rating):
        if not np.isfinite(rating.max):
            return 1
        return (rating.max - rating.value) / 2

    def user_learn(self,
        user: User, # not used
        entities: Entities, # not used
        ratings: Ratings, # keynames == ["criterion", "entity_name"]
        comparisons: Comparisons, # not used
        base_model: ScoringModel, # not used
    ) -> ScoringModel:
        model = ScoringModel()
        for keys, rating in ratings:
            kwargs = ratings.keys2kwargs(*keys)
            entity_name, criterion = kwargs["entity_name"], kwargs["criterion"]
            uncertainties = self.left_unc(rating), self.right_unc(rating)
            model[entity_name, criterion] = Score(rating.value, *uncertainties)
        return model