from typing import Optional, Mapping

import numpy as np
import pandas as pd

from solidago.state import *
from solidago.modules.base import StateFunction


class Squash(StateFunction):
    def __init__(self, score_max: float = 100.0):
        assert score_max > 0
        self.score_max = score_max
    
    def __call__(self, 
        user_models: UserModels,
        global_model: ScoringModel,
    ) -> tuple[UserModels, ScoringModel]:
        """ Post-processes user models and global models,
        typically to yield human-readible scores, 
        by squashing scores into [-self.score_max, self.score_max] """
        squashed_user_models = UserModels({
            username: SquashedModel(model, self.score_max) 
            for username, model in user_models
        })
        squashed_global_model = SquashedModel(global_model, self.score_max)
        return squashed_user_models, squashed_global_model
