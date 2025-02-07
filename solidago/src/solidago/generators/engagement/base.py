from numpy.random import random

from solidago.state import *
from solidago.modules import StateFunction


class EngagementGen(StateFunction):
    def __call__(self, users: Users, entities: Entities) -> tuple[MadePublic, Assessments, Comparisons]:
        made_public, assessments, comparisons = MadePublic(), Assessments(), Comparisons()
        for user in users:
            eval_entities = self.sample_evaluated_entities(user, entities)
            for index, entity in enumerate(eval_entities):
                public = self.public(user, entity, eval_entities)
                made_public.set(public, user, entity)
                assess = self.assess(user, entity, eval_entities)
                if assess:
                    assessments.add_row(user, "default", entity)
                for index2, entity2 in enumerate(eval_entities):
                    if index2 >= index:
                        break
                    compare = self.compare(user, entity, entity2, eval_entities)
                    if compare:
                        shuffle = self.shuffle(user, entity, entity2, eval_entities)
                        left, right = (entity, entity2) if shuffle else (entity2, entity)
                        comparisons.add_row(user, "default", left, right)
        return made_public, assessments, comparisons
        
    def sample_evaluated_entities(self, user: User, entities: Entities) -> Entities:
        return type(entities)([ e for e in entities if random() < 0.5 ])

    def public(self, user: User, entity: Entity, eval_entities: Entities) -> bool:
        return random() < 0.5

    def assess(self, user: User, entity: Entity, eval_entities: Entities) -> bool:
        return random() < 0.5
        
    def compare(self, user: User, entity1: Entity, entity2: Entity, eval_entities: Entities) -> bool:
        return random() < 0.5
        
    def shuffle(self, user: User, entity1: Entity, entity2: Entity, eval_entities: Entities) -> bool:
        return random() < 0.5
