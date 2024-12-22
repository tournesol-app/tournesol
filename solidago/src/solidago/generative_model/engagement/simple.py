from numpy.random import random, normal

import pandas as pd
import numpy as np

from solidago.state import Users, Entities, VotingRights, Judgments
from .base import EngagementGenerator


class SimpleComparisonOnlyEngagementGenerator(EngagementGenerator):
    def __init__(
        self, 
        p_per_criterion: dict[str, float]={"0": 1.0}, 
        p_private: float=0.2
    ):
        """ Simple Engagement defines a simple way for users to interact with entities.
        Requires NormalUser 
        
        Parameters
        ----------
        p_per_criterion: dict[str, float]
            p_per_criterion[criterion] is the probability that an entity gets compared on criterion
            Some "main" criterion may be given probability 1,
            while secondary criteria may be given a lower probability
        p_private: float
            Probability that a user engages with an entity privately
        """
        self.p_per_criterion = p_per_criterion
        self.p_private = p_private

    
    def __call__(self, users: Users, entities: Entities) -> tuple[Privacy, Judgments]:
        comparison_list = list()
        voting_rights = VotingRights()
        
        for user in users:
            if row["n_comparisons"] <= 0:
                continue
                
            n_compared_entities = int(2 * user["n_comparisons"] / user["n_comparisons_per_entity"] )
            p_compare_ab = 2 * row["n_comparisons"] / n_compared_entities**2
            
            scores = _svd_scores(user, users, entities)
            compared_list = _random_biased_order(scores, row["engagement_bias"])[:n_compared_entities]
            
            for index, e1 in enumerate(compared_list):
                privacy.set(user, e1, random() > self.p_private)
                for e2 in compared_list[index + 1:]:
                    if random() >= p_compare_ab:
                        continue
                    for criterion in self.p_per_criterion:
                        if random() <= self.p_per_criterion[criterion]:
                            if random() <= 0.5:
                                comparison_list.append((user, criterion, e1, e2))
                            else:
                                comparison_list.append((user, criterion, e2, e1))
        
        c = list(zip(*comparison_list))
        return privacy, DataFrameJudgments(pd.DataFrame(dict(
            user_id=c[0], criteria=c[1], entity_a=c[2], entity_b=c[3])))

    
    def __call__(self, users: Users, entities: Entities) -> tuple[VotingRights, Judgments]:
        """ Assigns a list of comparisons to be made to each entity, by each user """
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
        return f"SimpleEngagement({properties})"

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
    noisy_scores = np.array([- score_bias * scores[k] + normal() for k in keys])
    argsort = np.argsort(noisy_scores)
    return [keys[argsort[k]] for k in range(len(keys))]
