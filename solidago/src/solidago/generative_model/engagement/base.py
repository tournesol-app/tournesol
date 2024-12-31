from numpy.random import random

from solidago.state import *
from solidago.pipeline import StateFunction


class EngagementGenerator(StateFunction):
    def __call__(self, state: State) -> None:
        state.made_public = MadePublic()
        state.assessments, state.comparisons = Assessments(), Comparisons()
        for user in state.users:
            eval_entities = self.sample_evaluated_entities(state, user)
            for index, entity in enumerate(eval_entities):
                public = self.public(state, user, entity, eval_entities)
                state.made_public[user, entity] = public
                assess = self.assess(state, user, entity, eval_entities)
                if assess:
                    state.assessments.add(user, entity)
                for index2, entity2 in enumerate(eval_entities):
                    if index2 >= index:
                        break
                    compare = self.compare(state, user, entity, entity2, eval_entities)
                    if compare:
                        shuffle = self.shuffle(state, user, entity, entity2, eval_entities)
                        left, right = (entity, entity2) if shuffle else (entity2, entity)
                        state.comparisons.add(user, left, right)
        
    def sample_evaluated_entities(self, state: State, user: User) -> Entities:
        return type(state.entities)([ e for e in state.entities if random() < 0.5 ])

    def public(self, state: State, user: User, entity: Entity, eval_entities: Entities) -> bool:
        return random() < 0.5

    def assess(self, state: State, user: User, entity: Entity, eval_entities: Entities) -> bool:
        return random() < 0.5
        
    def compare(self, state: State, user: User, entity1: Entity, entity2: Entity, eval_entities: Entities) -> bool:
        return random() < 0.5
        
    def shuffle(self, state: State, user: User, entity1: Entity, entity2: Entity, eval_entities: Entities) -> bool:
        return random() < 0.5
