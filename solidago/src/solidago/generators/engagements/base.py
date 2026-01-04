from abc import abstractmethod
from typing import TYPE_CHECKING, Union

import numpy as np

from solidago.poll import *
from solidago.generators.generator import GeneratorStep

if TYPE_CHECKING:
    from .select_entities import SelectEntities


class Independent(GeneratorStep):
    """ 
    By default, sets
    user.p_public == 1.0
    user.p_assess == 0.0
    user.p_compare == 0.0
    user.n_comparisons_per_entity == 0.0
    """
    def __init__(self, 
        select_entities: Union["SelectEntities", list, tuple] | None = None,
        criteria: list[str] | None = None, # by default, will be set to ["default"]
        shuffle: bool = True
    ):
        from solidago.generators.engagements.select_entities import SelectEntities
        self.select_entities = SelectEntities.load(select_entities)
        self.shuffle = shuffle
        self.criteria = criteria or ["default"]

    def __call__(self, users: Users, entities: Entities) -> tuple[MadePublic, Assessments, Comparisons]:
        made_public, assessments, comparisons = MadePublic(), Assessments(), Comparisons()
        for user in users:
            evaluated_entities = self.select_entities(user, entities)
            self.user_engagement(user, evaluated_entities, made_public, assessments, comparisons)
        return made_public, assessments, comparisons

    def user_engagement(self, 
        user: User,
        eval_entities: Entities, 
        made_public: MadePublic, 
        assessments: Assessments, 
        comparisons: Comparisons,
    ) -> tuple[MadePublic, Assessments, Comparisons]:
        for entity in eval_entities:
            assert isinstance(entity, Entity)
            made_public[user, entity] = self.public(user, entity, eval_entities)
            if self.assess(user, entity, eval_entities):
                assessments[user, "default", entity] = Assessment()
        for left, right in eval_entities.iter_pairs(shuffle=True):
            if self.compare(user, left, right, eval_entities):
                comparisons[user, "default", left, right] = Comparison()
        return made_public, assessments, comparisons

    def public(self, user: User, entity: Entity, eval_entities: Entities) -> bool:
        p_public = user.p_public if hasattr(user, "p_public") else 1.0
        assert p_public >= 0.0, p_public
        return bool(np.random.random() < p_public)

    def assess(self, user: User, entity: Entity, eval_entities: Entities) -> bool:
        if not hasattr(user, "p_assess"):
            return False
        assert user.p_assess >= 0.0, user
        return bool(np.random.random() < user.p_assess)
        
    def compare(self, user: User, left: Entity, right: Entity, eval_entities: Entities) -> bool:
        if not hasattr(user, "p_compare") and not hasattr(user, "n_comparisons_per_entity"):
            return False
        if hasattr(user, "p_compare"):
            return np.random.random() < user.p_compare
        return bool(np.random.random() < user.n_comparisons_per_entity / len(eval_entities))
        