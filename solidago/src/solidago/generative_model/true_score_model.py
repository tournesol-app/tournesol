from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

class TrueScoreModel(ABC):
    @abstractmethod
    def __call__(self, users: pd.DataFrame, entities: pd.DataFrame) -> np.matrix:
        """ Assigns a score to each entity, by each user
        Inputs:
        - users: DataFrame with columns
            * `user_id`: int
            * `is_pretrusted`: bool
            * And maybe more
        - entities: DataFrame with columns
            * `entity_id`: int
            * And maybe more
        
        Returns:
        - scores, where scores[u][e] is the score given to entity e by user u
        """
        raise NotImplementedError
