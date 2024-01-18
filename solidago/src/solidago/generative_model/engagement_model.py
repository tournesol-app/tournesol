from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

class EngagementModel(ABC):
    @abstractmethod
    def __call__(
        self, 
        users: pd.DataFrame, 
        true_scores: pd.DataFrame
    ) -> tuple[dict[int, dict[int, bool]], pd.DataFrame]:
        """ Assigns a score to each entity, by each user
        
        Parameters
        ----------
        users: DataFrame
            Must have an index column `user_id`. May have others.
        true_scores: DataFrame
            true_scores.loc[u, e] is the true score assigned by user u (int) to entity e (int).
        
        Returns
        -------
        privacy: DataFrame with columns
            * `user_id`
            * `entity_id`
            * `is_public`
        comparisons: DataFrame with columns
            * `user_id`
            * `criteria`
            * `entity_a`
            * `entity_b`
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
        self.p_per_criterion = p_per_criterion
        self.p_public = p_public

    def __call__(
        self, 
        users: pd.DataFrame, 
        true_scores: pd.DataFrame
    ) -> tuple[dict[int, dict[int, bool]], pd.DataFrame]:
        """ Assigns a score to each entity, by each user
        Parameters
        ----------
        users: DataFrame with columns
            * `user_id`: int
            * `n_comparisons`: float
            * `n_comparisons_per_entity`: float
        true_scores: DataFrame
            true_scores.loc[u, e] is the true score assigned by user u (int) to entity e (int).
        
        Returns
        -------
        privacy: DataFrame with columns
            * `user_id``
            * `entity_id`
            * `is_public`
        comparisons: DataFrame with columns
            * `user_id`
            * `criteria`
            * `entity_a`
            * `entity_b`
        """
        n_entities = len(true_scores.columns)
        comparison_dct = dict(user_id=list(), criteria=list(), entity_a=list(), entity_b=list())
        privacy_dct = dict(user_id=list(), entity_id=list(), is_public=list())

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
                is_public = (np.random.random() <= self.p_public)
                privacy_dct["user_id"].append(user)
                privacy_dct["entity_id"].append(a)
                privacy_dct["is_public"].append(is_public)
                for b in range(a + 1, len(compared)):
                    if np.random.random() >= p_compare_ab:
                        continue
                    for c in self.p_per_criterion:
                        if np.random.random() <= self.p_per_criterion[c]:
                            comparison_dct["user_id"].append(user)
                            comparison_dct["criteria"].append(c)
                            if np.random.random() <= 0.5:
                                comparison_dct["entity_a"].append(a)
                                comparison_dct["entity_b"].append(b)
                            else:
                                comparison_dct["entity_a"].append(b)
                                comparison_dct["entity_b"].append(a)

        return pd.DataFrame(privacy_dct), pd.DataFrame(comparison_dct)

    def __str__(self):
        properties = f"p_per_criterion={self.p_per_criterion}, p_public={self.p_public}"
        return f"SimpleEngagementModel({properties})"
