from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import logging

logger = logging.getLogger(__name__)

from solidago.state import *
from solidago.pipeline.base import StateFunction


class PreferenceLearning(StateFunction, ABC):
    def __call__(self, 
        users: Users,
        entities: Entities,
        assessments: Assessments,
        comparisons: Comparisons,
        user_models: UserModels
    ) -> UserModels:
        """ Learns a scoring model, given user judgments of entities """
        learned_models = UserModels()
        comparison_key_names = ["username", "criterion", "left_name", "right_name"]
        reordered_comparisons = comparisons.reorder_keys(comparison_key_names)
        for user in users:
            learned_models[str(user)] = self.user_learn(
                user, 
                entities, 
                assessments[user], 
                comparisons[user],
                user_models[user].base_model() if user in user_models else DirectScoring()
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
