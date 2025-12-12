from abc import abstractmethod
from typing import TYPE_CHECKING, Union

import numpy as np

from solidago.poll import *
from solidago.generators.generator import GeneratorStep

if TYPE_CHECKING:
    from .select_entities import SelectEntities


class Independent(GeneratorStep):
    """ Requires users.{n_evaluated_entities, p_public, p_assess, {p_compare or n_comparisons_per_entity}} """
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
        assert hasattr(user, "p_public") and user.p_public >= 0.0
        return bool(np.random.random() < user.p_public)

    def assess(self, user: User, entity: Entity, eval_entities: Entities) -> bool:
        assert hasattr(user, "p_assess") and user.p_assess >= 0.0
        return bool(np.random.random() < user.p_assess)
        
    def compare(self, user: User, left: Entity, right: Entity, eval_entities: Entities) -> bool:
        assert hasattr(user, "p_compare") or hasattr(user, "n_comparisons_per_entity")
        if hasattr(user, "p_compare"):
            return np.random.random() < user.p_compare
        return bool(np.random.random() < user.n_comparisons_per_entity / len(eval_entities))
        