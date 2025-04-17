from abc import ABC, abstractmethod
import numpy as np

from solidago.state import *
from solidago.modules.base import StateFunction


class CollaborativeFiltering(StateFunction, ABC):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, users: Users, entities: Entities, user_models: UserModels) -> UserModels:
        user_directs = MultiScore(["criterion", "username", "entity_name"])
        for criterion in user_models.criteria():
            user_directs[criterion] = self.fill_criterion(users, entities, user_models, criterion)
        return UserModels(user_directs=user_directs.reorder("username", "entity_name", "criterion"))
    
    def fill_criterion(self, 
        users: Users, 
        entities: Entities, 
        user_models: UserModels, 
        criterion: str
    ) -> MultiScore:
        matrices = user_models.to_matrices(users, entities, criterion)
        value_matrix, left_matrix, right_matrix = self.fill(*matrices)
        scores = MultiScore(["username", "entity_name"])
        for user_index in range(value_matrix.shape[0]):
            username = users.index2name(user_index)
            for entity_index in range(value_matrix.shape[1]):
                entity_name = entities.index2name(entity_index)
                value = value_matrix[user_index, entity_index]
                left = left_matrix[user_index, entity_index]
                right = right_matrix[user_index, entity_index]
                scores[username, entity_name] = Score(value, left, right)
        return scores
    
    @abstractmethod
    def fill(self, 
        value_matrix: np.ndarray, 
        left_matrix: np.ndarray, 
        right_matrix: np.ndarray
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        raise NotImplemented

    def save_result(self, state: State, directory: Optional[str]=None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving user base model")
            state.user_models.save_base_models(directory)
        logger.info("Saving state.json")
        return state.save_instructions(directory)