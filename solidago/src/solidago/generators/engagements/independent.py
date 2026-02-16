from typing import TYPE_CHECKING, Union

import numpy as np

from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction

if TYPE_CHECKING:
    from .select_entities import SelectEntities


class Independent(PollFunction):
    """ 
    By default, sets
    user.p_public == 1.0
    user.p_rate == 0.0
    user.p_compare == 0.0
    user.n_comparisons_per_entity == 0.0
    """
    def __init__(self, 
        select_entities: Union["SelectEntities", list, tuple],
        criteria: list[str] | None = None, # by default, will be set to ["default"]
        shuffle: bool = True
    ):
        from solidago.generators.engagements.select_entities import SelectEntities
        self.select_entities = SelectEntities.load(select_entities)
        self.shuffle = shuffle
        self.criteria = criteria or ["default"]

    def __call__(self, users: Users, entities: Entities) -> tuple[PublicSettings, Ratings, Comparisons]:
        public_settings, ratings, comparisons = PublicSettings(), Ratings(), Comparisons()
        for user in users:
            evaluated_entities = self.select_entities(user, entities)
            self.user_engagement(user, evaluated_entities, public_settings, ratings, comparisons)
        return public_settings, ratings, comparisons

    def user_engagement(self, 
        user: User,
        eval_entities: Entities, 
        public_settings: PublicSettings, 
        ratings: Ratings, 
        comparisons: Comparisons,
    ) -> tuple[PublicSettings, Ratings, Comparisons]:
        for entity in eval_entities:
            assert isinstance(entity, Entity)
            public = self.public(user, entity, eval_entities)
            public_settings.set(username=user.name, entity_name=entity.name, public=public)
            if self.rate(user, entity, eval_entities):
                ratings.set(username=user.name, criterion="default", entity_name=entity.name)
        for left, right in eval_entities.iter_pairs(shuffle=True):
            if self.compare(user, left, right, eval_entities):
                comparisons.set(username=user.name, criterion="default", left_name=left.name, right=right.name)
        return public_settings, ratings, comparisons

    def public(self, user: User, entity: Entity, eval_entities: Entities) -> bool:
        p_public = user["p_public"] if "public" in user else 1.0
        assert p_public >= 0.0, p_public
        return bool(np.random.random() < p_public)

    def rate(self, user: User, entity: Entity, eval_entities: Entities) -> bool:
        if not hasattr(user, "p_rate"):
            return False
        assert user["p_rate"] >= 0.0, user
        return bool(np.random.random() < user["p_rate"])
        
    def compare(self, user: User, left: Entity, right: Entity, eval_entities: Entities) -> bool:
        if not hasattr(user, "p_compare") and not hasattr(user, "n_comparisons_per_entity"):
            return False
        if hasattr(user, "p_compare"):
            return np.random.random() < user["p_compare"]
        return bool(np.random.random() < user["n_comparisons_per_entity"] / len(eval_entities))
        