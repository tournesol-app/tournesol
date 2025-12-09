from typing import Optional, Mapping

import numpy as np
import pandas as pd

from solidago.poll import *
from solidago.modules.base import PollFunction


class Squash(PollFunction):
    def __init__(self, score_max: float = 100.0, *args, **kwargs):
        assert score_max > 0
        super().__init__(*args, **kwargs)
        self.score_max = score_max
    
    def __call__(self, 
        user_models: UserModels,
        global_model: ScoringModel,
    ) -> tuple[UserModels, ScoringModel]:
        """ Post-processes user models and global models,
        typically to yield human-readible scores, 
        by squashing scores into [-self.score_max, self.score_max] """
        return user_models.squash(self.score_max, "squash"), global_model.squash(self.score_max, "squash")

    def save_result(self, poll: Poll, directory: Optional[str]=None) -> tuple[str, dict]:
        return poll.save_instructions(directory)
