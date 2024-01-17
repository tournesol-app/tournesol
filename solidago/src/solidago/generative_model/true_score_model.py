from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

class TrueScoreModel(ABC):
    @abstractmethod
    def __call__(self, users: pd.DataFrame, entities: pd.DataFrame) -> pd.DataFrame:
        """ Assigns a score to each entity, by each user
        
        Parameters
        ----------
        users: DataFrame with columns
            * `user_id`: int
            * `is_pretrusted`: bool
            * And maybe more
        entities: DataFrame with columns
            * `entity_id`: int
            * And maybe more
        
        Returns
        -------
        scores: DataFrame with n_entities columns
            scores.loc[u, e] is the score given to entity e by user u
        """
        raise NotImplementedError

    def __str__(self):
        return type(self).__name__
        
class SvdTrueScoreModel(TrueScoreModel):
    def __init__(self, noise_scale: float = 0.5):
        self.noise_scale = noise_scale
        
    def __call__(self, users: pd.DataFrame, entities: pd.DataFrame) -> pd.DataFrame:
        """ 
        Generates true scores, obtained by adding a noise to the scalar product
        between the users' and entities' vector representations.
        
        Parameters
        ----------
        users: DataFrame with columns
            * `user_id`: int
            * `is_pretrusted`: bool
            * And maybe more
        entities: DataFrame with columns
            * `entity_id`: int
            * And maybe more
        
        Returns
        -------
        scores: DataFrame with n_entities columns
            scores.loc[u, e] is the score given to entity e by user u
        """
        svd_dimension, svd_columns = 0, list()
        while True:
            column = f"svd{svd_dimension}"
            if column not in users or column not in entities:
                break
            svd_columns.append(column)
            svd_dimension += 1

        scores = users[svd_columns] @ entities[svd_columns].T / svd_dimension
        scores += np.random.normal(0, self.noise_scale, (len(users), len(entities)))
        return scores

    def __str__(self):
        return f"SvdTrueScoreModel(noise_scale={self.noise_scale})"
        
