from abc import ABC, abstractmethod
from typing import Mapping

import pandas as pd

from solidago.state import *


class PostProcess(StateFunction):
    def main(self, 
        user_models: UserModels,
        global_model: ScoringModel,
    ) -> tuple[UserModels, ScoringModel]:
        """ Post-processes user models and global models,
        typically to yield human-readible scores """
        return user_models, global_model
