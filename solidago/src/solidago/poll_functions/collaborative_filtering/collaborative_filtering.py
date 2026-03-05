from abc import ABC, abstractmethod
from numpy.typing import NDArray

import numpy as np
import logging

logger = logging.getLogger(__name__)

from solidago.poll import *
from solidago.poll.scoring import *
from solidago.poll_functions.poll_function import PollFunction


class CollaborativeFiltering(PollFunction, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def fn(self, users: Users, entities: Entities, user_models: UserModels) -> UserModels:
        user_directs = UserDirectScores()
        for criterion in user_models.criteria():
            self.fill_criterion(users, entities, user_models, criterion, user_directs)
        return UserModels(user_directs=user_directs)
    
    def fill_criterion(self, 
        users: Users, 
        entities: Entities, 
        user_models: UserModels, 
        criterion: str,
        user_directs: UserDirectScores,
    ):
        matrices = user_models.to_matrices(users, entities, criterion)
        value_matrix, left_matrix, right_matrix = self.fill(*matrices)
        for user_index in range(value_matrix.shape[0]):
            username = users.index2name(user_index)
            for entity_index in range(value_matrix.shape[1]):
                user_directs.set(
                    username = username,
                    entity_name = entities.index2name(entity_index),
                    value = value_matrix[user_index, entity_index],
                    left = left_matrix[user_index, entity_index],
                    right = right_matrix[user_index, entity_index],
                )
    
    @abstractmethod
    def fill(self, 
        value_matrix: NDArray, 
        left_matrix: NDArray, 
        right_matrix: NDArray
    ) -> tuple[NDArray, NDArray, NDArray]:
        raise NotImplemented

    def save_result(self, poll: Poll, directory: str | None=None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving user base model")
            poll.user_models.save_table(directory, "user_directs")
        return poll.save_instructions(directory)