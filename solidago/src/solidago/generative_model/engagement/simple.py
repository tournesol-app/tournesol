from typing import Union
from numpy.random import random, normal

import pandas as pd
import numpy as np

from solidago.state import Users, Entities, Privacy, Assessments, Comparisons, Judgments
from .base import EngagementGenerator


class SimpleEngagementGenerator(EngagementGenerator):
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
        privacy, assessments, comparisons = Privacy(), list(), list()
        entity_index2id = { entity["vector_index"]: entity.id for entity in entities }
        
        for user in users:
            if user["n_comparisons"] <= 0:
                continue
    
            n_compared_entities = int(2 * user["n_comparisons"] / user["n_comparisons_per_entity"] )
            n_compared_entities = min(len(entities), n_compared_entities)
            p_compare_ab = 2 * user["n_comparisons"] / n_compared_entities**2

            # To implement engagement bias, we construct a noisy score-based sort of the entities
            scores = entities.vectors @ user.vector
            noisy_scores = - user["engagement_bias"] * scores + normal(0, 1, len(scores))
            argsort = np.argsort(noisy_scores)
            compared_entities = [ entity_index2id[argsort[i]] for i in range(n_compared_entities) ]

            for index, e1 in enumerate(compared_entities):
                privacy[user, e1] = (random() < self.p_private)
                for criterion in self.p_assessment_per_criterion:
                    if random() > self.p_comparison_per_criterion[criterion]:
                        continue
                    assessments.append({ "username": user.name, "criterion": criterion, "entity_id": e1 })
                for e2 in compared_entities[index + 1:]:
                    if random() >= p_compare_ab:
                        continue
                    for criterion in self.p_comparison_per_criterion:
                        if random() >= self.p_comparison_per_criterion[criterion]:
                            continue
                        shuffle_1_2 = (random() < 0.5)
                        comparisons.append({
                            "username": user.name, 
                            "criterion": criterion,
                            "left_id": e1 if shuffle_1_2 else e2,
                            "right_id": e2 if shuffle_1_2 else e1
                        })
        
        return privacy, Judgments(Assessments(assessments), Comparisons(comparisons))

    def __str__(self):
        properties = ", ".join([f"{key}={value}" for key, value in self.__dict__.items()])
        return f"SimpleEngagementGenerator({properties})"

    def to_json(self):
        return type(self).__name__, self.__dict__
        
