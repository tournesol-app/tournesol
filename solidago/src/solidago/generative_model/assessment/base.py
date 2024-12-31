import numpy as np

from solidago.state import *
from solidago.pipeline import StateFunction


class AssessmentGenerator(StateFunction):
    def __call__(self, state: State) -> None:
        """ Fills in the assessments """
        for (username, entity_name), assessment_list in state.assessments:
            for index, assessment in enumerate(assessment_list):
                user = state.users.get(username)
                entity = state.entities.get(entity_name)
                public = state.made_public[user, entity]
                a, a_min, a_max = self.sample(state, assessment, user, entity, public)
                state.assessments[user, entity][index] |= { 
                    "assessment": a,
                    "assessment_min": a_min, 
                    "assessment_max": a_max, 
                }
        
    def sample(self, state: State, assessment: Assessment, user: User, entity: Entity, public: bool) -> tuple[float, float, float]:
        """ Returns assessment min, max and value """
        return np.random.random(), 0, 1
