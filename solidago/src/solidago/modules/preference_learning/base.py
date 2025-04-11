from abc import ABC, abstractmethod
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

import pandas as pd
import logging

logger = logging.getLogger(__name__)

from solidago.state import *
from solidago.modules.base import StateFunction



class PreferenceLearning(StateFunction, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, 
        users: Users,
        entities: Entities,
        assessments: Assessments,
        comparisons: Comparisons,
        user_models: UserModels
    ) -> UserModels:
        """ Learns a scoring model, given user judgments of entities """
        learned_models = UserModels()
        args_list = [
            (user, entities, assessments[user], comparisons[user], user_models[user].base_model())
            for user in users
        ]
        with ThreadPoolExecutor(max_workers=self.max_workers) as e:
            futures = {e.submit(self.user_learn, *args): args for args in args_list}
            for f in as_completed(futures):
                user = futures[f][0]
                learned_models[user] = f.result()
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
