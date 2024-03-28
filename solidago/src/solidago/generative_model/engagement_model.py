from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import Judgments, DataFrameJudgments


class EngagementModel(ABC):
    @abstractmethod
    def __call__(
        self, 
        users: pd.DataFrame, 
        entities: pd.DataFrame
    ) -> tuple[PrivacySettings, Judgments]:
        """ Assigns a score to each entity, by each user
        
        Parameters
        ----------
        users: DataFrame
            Must have an index column `user_id`. May have others.
        entities: DataFrame with columns
            * `entity_id`: int
            * And maybe more
        
        Returns
        -------
        privacy: PrivacySettings
            privacy[user][entity] may be True (private), False (public) or None (undefined).
        judgments: Judgments
            judgments[user]["comparisons"] yields the user's comparisons
            judgments[user]["assessments"] yields the user's assessments
        """
        raise NotImplementedError

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )

                
class SimpleEngagementModel(EngagementModel):
    def __init__(
        self, 
        p_per_criterion: dict[str, float]={"0": 1.0}, 
        p_private: float=0.2
    ):
        self.p_per_criterion = p_per_criterion
        self.p_private = p_private

    def __call__(
        self, 
        users: pd.DataFrame, 
        entities: pd.DataFrame
    ) -> tuple[PrivacySettings, DataFrameJudgments]:
        """ Assigns a list of comparisons to be made to each entity, by each user
        
        Parameters
        ----------
        users: DataFrame with columns
            * `user_id`: int
            * `n_comparisons`: float
            * `n_comparisons_per_entity`: float
        entities: DataFrame with columns
            * `entity_id`: int
        
        Returns
        -------
        privacy: PrivacySettings
            privacy[user][entity] may be True (private), False (public) or None (undefined).
        judgments: DataFrameJudgments
            judgments[user]["comparisons"] yields the user's comparisons
            judgments[user]["assessments"] yields the user's assessments
        """
        comparison_list = list()
        privacy = PrivacySettings()
        
        for user, row in users.iterrows():
            if row["n_comparisons"] <= 0:
                continue
                
            n_compared_entities = 2 * row["n_comparisons"]
            n_compared_entities /= row["n_comparisons_per_entity"]
            n_compared_entities = int(n_compared_entities)
            
            p_compare_ab = 2 * row["n_comparisons"] 
            p_compare_ab /= n_compared_entities**2
            
            scores = _svd_scores(user, users, entities)
            compared_list = _random_biased_order(scores, row["engagement_bias"])
            compared_list = compared_list[:n_compared_entities]
            for a_index, a in enumerate(compared_list):
                privacy[user, a] = (np.random.random() <= self.p_private)
                for b in compared_list[a_index + 1:]:
                    if np.random.random() >= p_compare_ab:
                        continue
                    for criterion in self.p_per_criterion:
                        if np.random.random() <= self.p_per_criterion[criterion]:
                            if np.random.random() <= 0.5:
                                comparison_list.append((user, criterion, a, b))
                            else:
                                comparison_list.append((user, criterion, b, a))
        
        c = list(zip(*comparison_list))
        return privacy, DataFrameJudgments(pd.DataFrame(dict(
            user_id=c[0], criteria=c[1], entity_a=c[2], entity_b=c[3])))

    def __str__(self):
        properties = f"p_per_criterion={self.p_per_criterion}, p_private={self.p_private}"
        return f"SimpleEngagementModel({properties})"

    def to_json(self):
        return type(self).__name__, dict(
            p_per_criterion=self.p_per_criterion, 
            p_private=self.p_private
        )
        
def _svd_scores(user, users, entities):
    svd_cols, svd_dim = list(), 0
    while f"svd{svd_dim}" in users and f"svd{svd_dim}" in entities:
        svd_cols.append(f"svd{svd_dim}")
        svd_dim += 1
        
    if svd_dim == 0:
        return { e: 0 for e in entities.index }
        
    user_svd = users[svd_cols].loc[user]
    return {
        entity: (user_svd @ entities[svd_cols].loc[entity]) / svd_dim
        for entity, _ in entities.iterrows()
    }

def _random_biased_order(scores: dict[int, float], score_bias: float) -> list[int]:
    """
    Parameters
    ----------
    scores: dict
        scores[entity] is the score of the entity
    bias: float
        Larger biases must imply a more deterministic order
    """
    keys = list(scores.keys())
    noisy_scores = np.array([- score_bias * scores[k] + np.random.normal() for k in keys])
    argsort = np.argsort(noisy_scores)
    return [keys[argsort[k]] for k in range(len(keys))]
