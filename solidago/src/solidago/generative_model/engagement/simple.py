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
        p_assessment: float=1.0, 
        p_comparison: float=1.0,
    ):
        """ Simple Engagement defines a simple way for users to interact with entities.
        Requires NormalUser 
        
        Parameters
        ----------
        p_public: float
            Probability that a user engages with an entity publicly
        p_comparison: float
            p_per_criterion[criterion] is the probability that an entity gets compared on criterion
            Some "main" criterion may be given probability 1,
            while secondary criteria may be given a lower probability
        p_assessment: float
            p_per_criterion[criterion] is the probability that an entity gets compared on criterion
            Some "main" criterion may be given probability 1,
            while secondary criteria may be given a lower probability
        """
        self.p_public = p_public
        self.p_assessment = p_assessment
        self.p_comparison = p_comparison

    def __call__(self, 
        users: Users, 
        entities: Entities, 
        criteria: Criteria
    ) -> tuple[MadePublic, Assessments, Comparisons]:
        made_public, assessments, comparisons = MadePublic(), dict(), dict()
        entity_index2id = { entity["vector_index"]: str(entity) for entity in entities }
        
        for user in users:
            if user["n_comparisons"] <= 0:
                continue
            
            assessments, comparisons = Assessments(), Comparisons()
            n_compared_entities = int(2 * user["n_comparisons"] / user["n_comparisons_per_entity"] )
            n_compared_entities = min(len(entities), n_compared_entities)
            p_compare_ab = 2 * user["n_comparisons"] / n_compared_entities**2

            # To implement engagement bias, we construct a noisy score-based sort of the entities
            scores = entities.vectors @ user.vector
            noisy_scores = - user["engagement_bias"] * scores + normal(0, 1, len(scores))
            argsort = np.argsort(noisy_scores)
            compared_entities_names = [ entity_index2id[argsort[i]] for i in range(n_compared_entities) ]
            
            for entity_name in compared_entities_names:
                made_public[user, entity_name] = (random() < self.p_public)

            for criterion in criteria:
                for index, e1 in enumerate(compared_entities_names):
                    if random() > self.p_assessment:
                        continue
                    assessments[str(user), e1, str(criterion)] = float("nan"), float("nan"), float("nan")
                    for e2 in compared_entities_names[index + 1:]:
                        if random() >= p_compare_ab or random() >= self.p_comparison:
                            continue
                        left, right = (e1, e2) if (random() < 0.5) else (e2, e1)
                        comparisons[str(user), str(criterion), left, right] = float("nan"), float("nan")
        
        return made_public, assessments, comparisons

    def __str__(self):
        properties = ", ".join([f"{key}={value}" for key, value in self.__dict__.items()])
        return f"SimpleEngagementGenerator({properties})"

    def to_json(self):
        return type(self).__name__, self.__dict__
        
