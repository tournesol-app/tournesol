from abc import ABC, abstractmethod
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import logging
import os

logger = logging.getLogger(__name__)

from solidago.state import *
from solidago.modules.base import StateFunction



class PreferenceLearning(StateFunction, ABC):
    def __init__(self, max_workers: int=1):
        self.max_workers = max(1, min(max_workers, os.cpu_count() or 1))
    
    def __call__(self, 
        users: Users,
        entities: Entities,
        assessments: Assessments,
        comparisons: Comparisons,
        user_models: UserModels
    ) -> UserModels:
        """ Learns a scoring model, given user judgments of entities """
        learned_models = UserModels()
        args = lambda user: (assessments[user], comparisons[user], user_models[user].base_model())
        with ThreadPoolExecutor(max_workers=self.max_workers) as e:
            futures = [ e.submit(self.user_learn, user, entities, *args(user)) for user in users ]
            for user, future in zip(users, as_completed(futures)):
                learned_models[user] = future.result()
        return learned_models

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
