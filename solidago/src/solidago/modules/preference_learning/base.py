from abc import ABC, abstractmethod
from typing import Optional

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
        args = users, entities, assessments, comparisons, user_models

        if self.max_workers == 1:
            for username, score in self.batch(0, *args).items():
                learned_models[username] = score
            return learned_models

        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=self.max_workers) as e:
            futures = {e.submit(self.batch, i, *args) for i in range(self.max_workers)}
            results = [f.result() for f in as_completed(futures)]
        for result in results:
            for username, model in result.items():
                learned_models[username] = model
        return learned_models

    def batch(self, 
        batch_number: int,
        users: Users,
        entities: Entities,
        assessments: Assessments, # key_names == ["username", "criterion", "entity_name"]
        comparisons: Comparisons, # key_names == ["username", "criterion", "entity_name"]
        user_models: UserModels, # key_names == ["username", "criterion", "entity_name"]
    ) -> dict[str, ScoringModel]:
        indices = range(batch_number, len(users), self.max_workers)
        batch_users = {users.get_by_index(i) for i in indices}
        return {
            user.name: self.user_learn(
                user, 
                entities, 
                assessments[user], 
                comparisons[user], 
                user_models[user].base_model()
            ) for user in batch_users
        }

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

    def save_result(self, state: State, directory: Optional[str]=None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving user base model")
            state.user_models.save_base_models(directory)
        logger.info("Saving state.json")
        return state.save_instructions(directory)