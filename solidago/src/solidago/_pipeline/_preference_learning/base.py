from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import logging

logger = logging.getLogger(__name__)

from solidago._state import *
from solidago._pipeline.base import StateFunction


class PreferenceLearning(StateFunction, ABC):
    def __call__(self, 
        users: Users,
        entities: Entities,
        assessments: Assessments,
        comparisons: Comparisons,
        user_models: UserModels
    ) -> UserModels:
        """ Learns a scoring model, given user judgments of entities """
        result = UserModels()
        assessments = assessments.reorder_keys(["username", "criterion", "entity_name"])
        comparisons = comparisons.reorder_keys(["username", "criterion", "left_name", "right_name"])
        for user in users:
            logger.info(f"  Learning user {user}'s base model")
            result[user] = self.user_learn(user, entities, assessments[user], comparisons[user],
                user_models[user].base_model()[0])
        return result

    @abstractmethod
    def user_learn(self,
        user: User,
        entities: Entities,
        assessments: Assessments, # key_names == ["criterion", "entity_name"]
        comparisons: Comparisons, # key_names == ["criterion", "left_name", "right_name"]
        base_model: BaseModel
    ) -> BaseModel:
        """Learns a scoring model, given user judgments of entities """
        raise NotImplementedError
