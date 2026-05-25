import numpy as np

from solidago.poll import *
from .preference_learning import PreferenceLearning


class IsRating(PreferenceLearning):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def left_unc(self, rating: Rating):
        rating_min = rating.get("min", - np.inf)
        if not np.isfinite(rating_min):
            return 1
        return (rating["value"] - rating_min) / 2
    
    def right_unc(self, rating: Rating):
        rating_max = rating.get("max", np.inf)
        if not np.isfinite(rating_max):
            return 1
        return (rating_max - rating["value"]) / 2

    def user_learn(self,
        user: User, # not used
        entities: Entities, # not used
        ratings: Ratings, # keynames == ["criterion", "entity_name"]
        comparisons: Comparisons, # not used
        base_model: ScoringModel, # not used
    ) -> ScoringModel:
        model = ScoringModel()
        for r in ratings:
            score = Score((r["value"], self.left_unc(r), self.right_unc(r)))
            model.directs.set(score, entity_name=r["entity_name"], criterion=r["criterion"])
        return model