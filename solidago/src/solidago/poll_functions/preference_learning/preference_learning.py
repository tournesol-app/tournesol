from abc import ABC, abstractmethod
from typing import Optional

import logging

logger = logging.getLogger(__name__)

from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction


class PreferenceLearning(PollFunction, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, 
        users: Users,
        entities: Entities,
        ratings: Ratings,
        comparisons: Comparisons,
        user_models: UserModels
    ) -> UserModels:
        """ Learns a scoring model, given user judgments of entities """        
        models = [
            self.user_learn(
                user, 
                entities, 
                ratings.filters(username=user.name), 
                comparisons.filters(username=user.name), 
                user_models[user].base_model()
            ) 
            for user in users
        ]
        from solidago.poll.scoring.user_models import UserDirectScores
        user_directs = UserDirectScores()
        for user, model in zip(users, models):
            user_directs = user_directs | model.directs.add_columns(username=user.name)

        return UserModels(user_directs=user_directs)

    def batch(self, 
        batch_number: int,
        users: Users,
        entities: Entities,
        ratings: Ratings, # keynames == ["username", "criterion", "entity_name"]
        comparisons: Comparisons, # keynames == ["username", "criterion", "entity_name"]
        user_models: UserModels, # keynames == ["username", "criterion", "entity_name"]
    ) -> dict[str, ScoringModel]:
        indices = range(batch_number, len(users), self.max_workers)
        batch_users = users[indices]
        assert isinstance(batch_users, Users)
        return {
            user.name: self.user_learn(
                user, 
                entities, 
                ratings.filters(username=user.name), 
                comparisons.filters(username=user.name), 
                user_models[user].base_model()
            ) for user in batch_users
        }

    @abstractmethod
    def user_learn(self,
        user: User,
        entities: Entities,
        ratings: Ratings, # keynames == ["criterion", "entity_name"]
        comparisons: Comparisons, # keynames == ["criterion", "left_name", "right_name"]
        base_model: ScoringModel
    ) -> ScoringModel:
        """Learns a scoring model, given user judgments of entities """
        raise NotImplementedError

    def save_result(self, poll: Poll, directory: Optional[str]=None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving user base model")
            poll.user_models.save_table(directory, "user_directs")
        logger.info("Saving poll.yaml")
        return poll.save_instructions(directory)