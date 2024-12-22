from numpy.random import random, normal

import pandas as pd
import numpy as np

from solidago.state import Users, Entities, VotingRights, Comparisons, Judgments
from .base import EngagementGenerator


class SimpleComparisonOnlyEngagementGenerator(EngagementGenerator):
    def __init__(
        self, 
        p_private: float=0.2,
        p_comparison_per_criterion: dict[str, float]={"main": 1.0}, 
        p_assessment_per_criterion: dict[str, float]={"main": 0.0}, 
    ):
        """ Simple Engagement defines a simple way for users to interact with entities.
        Requires NormalUser 
        
        Parameters
        ----------
        p_private: float
            Probability that a user engages with an entity privately
        p_comparison_per_criterion: dict[str, float]
            p_per_criterion[criterion] is the probability that an entity gets compared on criterion
            Some "main" criterion may be given probability 1,
            while secondary criteria may be given a lower probability
        p_assessment_per_criterion: dict[str, float]
            p_per_criterion[criterion] is the probability that an entity gets compared on criterion
            Some "main" criterion may be given probability 1,
            while secondary criteria may be given a lower probability
        """
        self.p_private = p_private
        self.p_comparison_per_criterion = p_comparison_per_criterion
        self.p_assessment_per_criterion = p_assessment_per_criterion

    
    def __call__(self, users: Users, entities: Entities) -> tuple[Privacy, Judgments]:
        assessment_list, comparison_list = list(), list() # collects all added assesments/comparisons
        privacy = Privacy()
        
        for user in users:
            if row["n_comparisons"] <= 0:
                continue
                
            n_compared_entities = int(2 * user["n_comparisons"] / user["n_comparisons_per_entity"] )
            p_compare_ab = 2 * row["n_comparisons"] / n_compared_entities**2
            
            scores = _svd_scores(user, users, entities)
            compared_entities = _random_biased_order(scores, row["engagement_bias"])[:n_compared_entities]
            
            for index, e1 in enumerate(compared_entities):
                privacy[user, e1] = (random() > self.p_private)
                for criterion in self.p_assessment_per_criterion:
                    if random() <= self.p_comparison_per_criterion[criterion]:
                        comparison_list.append((user, criterion, e1, None, None, None))
                for e2 in compared_list[index + 1:]:
                    if random() >= p_compare_ab:
                        continue
                    for criterion in self.p_comparison_per_criterion:
                        if random() <= self.p_comparison_per_criterion[criterion]:
                            if random() <= 0.5:
                                comparison_list.append((user, criterion, e1, e2, None, None))
                            else:
                                comparison_list.append((user, criterion, e2, e1, None, None))
        
        a, c = list(zip(*assessment_list)), list(zip(*comparison_list))
        assessment_df = pd.DataFrame(dict(
            username=a[0], 
            criterion=a[1], 
            entity_id=a[2], 
            assessment_min=c[4],
            assessment_max=c[4],
            assessment=c[5]
        ))
        comparisons_df = pd.DataFrame(dict(
            username=c[0], 
            criterion=c[1], 
            left_id=c[2], 
            right_id=c[3],
            comparison_max=c[4],
            comparison=c[5]
        ))
        return privacy, Judgments(Comparisons(comparisons_df), Assessment(assessment_df))

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
