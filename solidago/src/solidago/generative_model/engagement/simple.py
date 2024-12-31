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
        p_assessment: float
            Probability that an entity gets assessed
        p_comparison: float
            Probability that an entity gets compared
        """
        self.p_public = p_public
        self.p_assessment = p_assessment
        self.p_comparison = p_comparison

    def sample_evaluated_entities(self, state: State, user: User) -> Entities:
        if user["n_comparisons"] <= 0:
            return type(state.entities)()
        
        n_eval_entities = int(2 * user["n_comparisons"] / user["n_comparisons_per_entity"] )
        n_eval_entities = min(len(state.entities), n_eval_entities)
        p_compare_ab = 2 * user["n_comparisons"] / n_eval_entities**2

        # To implement engagement bias, we construct a noisy score-based sort of the entities
        scores = state.entities.vectors @ user.vector
        noisy_scores = - user["engagement_bias"] * scores + normal(0, 1, len(scores))
        argsort = np.argsort(noisy_scores)
        entity_index2id = { index: str(entity) for index, entity in enumerate(state.entities) }
        return [ entity_index2id[argsort[i]] for i in range(n_eval_entities) ]

    def public(self, state: State, user: User, entity: Entity, eval_entities: Entities) -> bool:
        return random() < self.p_public

    def assess(self, state: State, user: User, entity: Entity, eval_entities: Entities) -> bool:
        return random() < self.p_assessment
        
    def compare(self, state: State, user: User, entity1: Entity, entity2: Entity, eval_entities: Entities) -> bool:
        p_compare_ab = 2 * user["n_comparisons"] / len(eval_entities)**2
        return random() < p_compare_ab and random() < self.p_comparison
        
    def shuffle(self, state: State, user: User, entity1: Entity, entity2: Entity, eval_entities: Entities) -> bool:
        return random() < 0.5
