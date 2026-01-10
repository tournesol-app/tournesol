from abc import ABC, abstractmethod
from typing import Optional

import logging

from solidago.primitives.threading import threading
logger = logging.getLogger(__name__)

from solidago.poll import *
from solidago.functions.base import PollFunction

from solidago.primitives.timer import time


class PreferenceLearning(PollFunction, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, 
        users: Users,
        entities: Entities,
        assessments: Assessments,
        comparisons: Comparisons,
        user_models: UserModels
    ) -> tuple[Users, Entities, UserModels]:
        """ Learns a scoring model, given user judgments of entities """
        users_list = [user for user in users]
        entities_list = [entities] * len(users)
        assessments_list = [assessments.get(username=user).detach() for user in users]
        comparisons_list = [comparisons.get(username=user).detach() for user in users]
        user_models_list = [user_models[user].base_model() for user in users]
        args_lists = users_list, entities_list, assessments_list, comparisons_list, user_models_list
        
        models = threading(self.max_workers, self.user_learn, *args_lists)
        learned_models = UserModels()
        for user, model in zip(users, models):
            learned_models[user] = model

        args = users, entities, assessments, comparisons, user_models
        return self.add_user_stats(*args), self.add_entity_stats(*args), learned_models
    
    def add_user_stats(self, 
        users: Users,
        entities: Entities,
        assessments: Assessments,
        comparisons: Comparisons,
        user_models: UserModels,
    ) -> Users:
        evaluated_entities = lambda u: assessments[u].keys("entity_name") | comparisons[u].keys("entity_name")
        return users.assign(
            n_assessments=[len(assessments[u]) for u in users], 
            n_comparisons=[len(comparisons[u]) for u in users], 
            n_evaluated_entities=[len(evaluated_entities(u)) for u in users]
        )
    
    def add_entity_stats(self,
        users: Users,
        entities: Entities,
        assessments: Assessments,
        comparisons: Comparisons,
        user_models: UserModels,
    ) -> Users:
        assessments = assessments.reorder("entity_name", "username", "criterion")
        comparisons = comparisons.reorder("entity_name", "username", "criterion")
        evaluators = lambda e: assessments[e].keys("username") | comparisons[e].keys("username")
        return entities.assign(
            n_assessments=[len(assessments[e]) for e in entities], 
            n_comparisons=[len(comparisons[e]) for e in entities], 
            n_assessers=[len(assessments[e].keys("username")) for e in entities], 
            n_comparers=[len(comparisons[e].keys("username")) for e in entities], 
            n_evaluators=[len(evaluators(e)) for e in entities]
        )

    def batch(self, 
        batch_number: int,
        users: Users,
        entities: Entities,
        assessments: Assessments, # keynames == ["username", "criterion", "entity_name"]
        comparisons: Comparisons, # keynames == ["username", "criterion", "entity_name"]
        user_models: UserModels, # keynames == ["username", "criterion", "entity_name"]
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
        assessments: Assessments, # keynames == ["criterion", "entity_name"]
        comparisons: Comparisons, # keynames == ["criterion", "left_name", "right_name"]
        base_model: ScoringModel
    ) -> ScoringModel:
        """Learns a scoring model, given user judgments of entities """
        raise NotImplementedError

    def save_result(self, poll: Poll, directory: Optional[str]=None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving user base model")
            poll.user_models.save_base_models(directory)
        logger.info("Saving poll.yaml")
        return poll.save_instructions(directory)