from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import logging

logger = logging.getLogger(__name__)

from solidago.state import *
from solidago.modules.base import StateFunction


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
        for user in users:
            logger.info(f"  Learning user {user}'s base model")
            user_args = assessments[user], comparisons[user], user_models[user].base_model()
            result[user] = self.user_learn(user, entities, *user_args)
        return result

    @abstractmethod
    def user_learn(self,
        user: User,
        entities: Entities,
        assessments: Assessments, # key_names == ["criterion", "entity_name"]
        comparisons: Comparisons, # key_names == ["criterion", "left_name", "right_name"]
        base_model: ScoringModel
    ) -> ScoringModel:
        """Learns a scoring model, given user judgments of entities """
        raise NotImplementedError
