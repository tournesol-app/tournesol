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
            * `is_public`
        """
        raise NotImplementedError

    def __str__(self):
        return type(self).__name__
        
class SimpleEngagementModel(EngagementModel):
    def __init__(
        self, 
        p_per_criterion: dict[str, float] = {"0": 1.0}, 
        p_public: float = 0.8
    ):
        self.p_criteria = p_criteria
        self.p_public = p_public
            
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
            * `is_public`
        """
        n_entities = len(true_scores.columns)
        dct = dict(user_id=list(), criteria=list(), entity_a=list(), entity_b=list())
        
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
                        for c in self.p_per_criterion:
                            if np.random.random() <= self.p_per_criterion[c]:
                                dct["user_id"].append(user)
                                dct["criteria"].append(c)
                                dct["entity_a"].append(a)
                                dct["entity_b"].append(b)
                                dct["is_public"].append(np.random.random() <= self.p_public)
                                
        return pd.DataFrame(dct)

    def __str__(self):
        properties = f"n_criteria={self.n_criteria}, p_criteria={self.p_criteria}"
        return f"SimpleEngagementModel({properties})"
