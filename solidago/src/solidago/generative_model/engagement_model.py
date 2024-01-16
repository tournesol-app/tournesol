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

    def __str__(self):
        return type(self).__name__
        
class SimpleEngagementModel(EngagementModel):
    def __init__(self, n_criteria: int = 1, p_criteria: float = 1.0):
        self.n_criteria = n_criteria
        self.p_criteria = p_criteria
    
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
            * `criteria`
            * `entity_a`
            * `entity_b`
        """
        n_entities = len(true_scores.columns)
        comparisons = list()
        
        for user, row in users.iterrows():
            n_compared_entities = 2 * row["n_comparisons"]
            n_compared_entities /= row["n_comparisons_per_entity"]
            compared = list()
            for entity in range(n_entities):
                if np.random.random() <= n_compared_entities / n_entities:
                    compared.append(entity)
            if len(compared) <= 1:
                continue
            p_compare_ab = 2 * row["n_comparisons"] / len(compared)  / (len(compared) - 1)
            for a in range(len(compared)):
                for b in range(a + 1, len(compared)):
                    if np.random.random() <= p_compare_ab:
                        for c in range(self.n_criteria):
                            if np.random.random() <= self.p_criteria:
                                comparisons.append((user, c, a, b))

        c = np.array(comparisons).T
        return pd.DataFrame(dict(user_id=c[0], criteria=c[1], entity_a=c[2], entity_b=c[3]))

    def __str__(self):
        properties = f"n_criteria={self.n_criteria}, p_criteria={self.p_criteria}"
        return f"SimpleEngagementModel({properties})"
