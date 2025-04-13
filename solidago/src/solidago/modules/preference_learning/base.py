from abc import ABC, abstractmethod
from typing import Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

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
        batches = [list() for _ in range(2*self.max_workers)]
        args = lambda u: (u, entities, assessments[u], comparisons[u], user_models[u].base_model())
        for index, user in enumerate(users):
            batches[index % len(batches)].append(args(user))
        with ProcessPoolExecutor(max_workers=self.max_workers) as e:
            futures = {e.submit(self.batch_learn, batch) for batch in batches}
            for f in as_completed(futures):
                for username, model in f.result().items():
                    learned_models[username] = model
        return learned_models

    def batch_learn(self, args_list: list) -> dict[str, ScoringModel]:
        return {str(args[0]): self.user_learn(*args) for args in args_list}        

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
