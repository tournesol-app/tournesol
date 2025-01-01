from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import logging

logger = logging.getLogger(__name__)

from solidago.state import *



class PreferenceLearning(ABC):
    def main(self, 
        users: Users,
        entities: Entities,
        assessments: Assessments,
        comparisons: Comparisons,
        user_models: UserModels
    ) -> UserModels:
        """ Learns a scoring model, given user judgments of entities """
        learned_models = UserModels()
        for user in users:
            learned_models[user] = self.user_learn(
                user, 
                entities, 
                assessments[user], 
                comparisons[user],
                user_models[user].base_model() if user in user_models else None
            )
        return learned_models

    @abstractmethod
    def user_learn(self,
        user: User,
        entities: Entities,
        assessments: Assessments,
        comparisons: Comparisons,
        base_model: BaseModel
    ) -> BaseModel:
        """Learns a scoring model, given user judgments of entities """
        raise NotImplementedError
