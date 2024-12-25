from typing import Union
from numpy.random import random, normal

import pandas as pd
import numpy as np

from solidago.state import *
from .base import EngagementGenerator


class SimpleEngagementGenerator(EngagementGenerator):
    def __init__(
        self, 
        p_public: float=0.8,
        p_comparison_per_criterion: dict[str, float]={"main": 1.0}, 
        p_assessment_per_criterion: dict[str, float]={"main": 0.0}, 
    ):
        """ Simple Engagement defines a simple way for users to interact with entities.
        Requires NormalUser 
        
        Parameters
        ----------
        p_public: float
            Probability that a user engages with an entity publicly
        p_comparison_per_criterion: dict[str, float]
            p_per_criterion[criterion] is the probability that an entity gets compared on criterion
            Some "main" criterion may be given probability 1,
            while secondary criteria may be given a lower probability
        p_assessment_per_criterion: dict[str, float]
            p_per_criterion[criterion] is the probability that an entity gets compared on criterion
            Some "main" criterion may be given probability 1,
            while secondary criteria may be given a lower probability
        """
        self.p_public = p_public
        self.p_comparison_per_criterion = p_comparison_per_criterion
        self.p_assessment_per_criterion = p_assessment_per_criterion

    def __call__(self, users: Users, entities: Entities) -> tuple[MadePublic, Judgments]:
        made_public, assessments, comparisons = MadePublic(), dict(), dict()
        entity_index2id = { entity["vector_index"]: str(entity) for entity in entities }
        
        for user in users:
            if user["n_comparisons"] <= 0:
                continue
            
            assessments[str(user)] = { criterion_id: list() for criterion_id in self.p_assessment_per_criterion }
            comparisons[str(user)] = { criterion_id: list() for criterion_id in self.p_comparison_per_criterion }
            n_compared_entities = int(2 * user["n_comparisons"] / user["n_comparisons_per_entity"] )
            n_compared_entities = min(len(entities), n_compared_entities)
            p_compare_ab = 2 * user["n_comparisons"] / n_compared_entities**2

            # To implement engagement bias, we construct a noisy score-based sort of the entities
            scores = entities.vectors @ user.vector
            noisy_scores = - user["engagement_bias"] * scores + normal(0, 1, len(scores))
            argsort = np.argsort(noisy_scores)
            compared_entities_ids = [ entity_index2id[argsort[i]] for i in range(n_compared_entities) ]

            for index, e1_id in enumerate(compared_entities_ids):
                made_public[user, e1_id] = (random() < self.p_public)
                for criterion_id in self.p_assessment_per_criterion:
                    if random() > self.p_comparison_per_criterion[criterion_id]:
                        continue
                    assessments[str(user)][criterion_id].append({ "entity_id": e1_id })
                for e2_id in compared_entities_ids[index + 1:]:
                    if random() >= p_compare_ab:
                        continue
                    for criterion_id in self.p_comparison_per_criterion:
                        if random() >= self.p_comparison_per_criterion[criterion_id]:
                            continue
                        left_id, right_id = (e1_id, e2_id) if (random() < 0.5) else (e2_id, e1_id)
                        comparisons[str(user)][criterion_id].append({ "left_id": left_id, "right_id": right_id })
        
        return made_public, Judgments(
            AssessmentsDictionary(assessments), 
            ComparisonsDictionary(comparisons)
        )

    def __str__(self):
        properties = ", ".join([f"{key}={value}" for key, value in self.__dict__.items()])
        return f"SimpleEngagementGenerator({properties})"

    def to_json(self):
        return type(self).__name__, self.__dict__
        
