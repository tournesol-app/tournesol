from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

class EngagementModel(ABC):
    @abstractmethod
    def __call__(self, users: pd.DataFrame, true_scores: pd.DataFrame) -> pd.DataFrame:
        """ Assigns a score to each entity, by each user
        Inputs:
        - users: DataFrame with columns
            * `user_id`
            * And maybe others
        - true_scores[u][e] is the true score assigned by user u to entity e
        
        Returns:
        - comparisons: DataFrame with columns
            * `user_id`
            * `criteria`
            * `entity_a`
            * `entity_b`
        """
        raise NotImplementedError

class SimpleEngagementModel(EngagementModel):
    def __call__(self, users: pd.DataFrame, true_scores: pd.DataFrame) -> pd.DataFrame:
        """ Assigns a score to each entity, by each user
        Inputs:
        - users: DataFrame with columns
            * `user_id`: int
            * `n_comparisons`: float
            * `n_comparisons_per_entity`: float
        - true_scores[u][e] is the true score assigned by user u to entity e
        
        Returns:
        - comparisons: DataFrame with columns
            * `user_id`
            * `entity_a`
            * `entity_b`
        """
        n_entities = len(true_scores.columns)
        comparisons = list()
        
        for user, user_row in users.iterrows():
            n_compared_entities = 2 * user_row["n_comparisons"]
            n_compared_entities /= user_row["n_comparisons_per_entity"]
            compared = list()
            for entity in range(n_entities):
                if np.random.random() <= n_compared_entities / n_entities:
                    compared.append(entity)
            for a in range(len(compared)):
                for b in range(a + 1, len(compared)):
                    if np.random.random() <= user_row["n_comparisons"] / (len(compared) - 1):
                        comparisons.append((user, a, b))

        c = np.array(comparisons).T
        return pd.DataFrame(dict(user_id=c[0], entity_a=c[1], entity_b=c[2]))
