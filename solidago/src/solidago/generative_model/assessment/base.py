import numpy as np

from solidago.state import *
from solidago.pipeline import StateFunction


class AssessmentGenerator(StateFunction):
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        made_public: MadePublic, 
        assessments: Assessments
    ) -> Assessments:
        """ Fills in the assessments """
        filled_assessments = Assessments()
        for (username, criterion, entity_name), assessment_list in assessments:
            filled_assessments[username, criterion, entity_name] = list()
            for index, assessment in enumerate(assessment_list):
                user = users.get(username)
                entity = entities.get(entity_name)
                public = made_public[user, entity]
                a, a_min, a_max = self.sample(assessment, user, entity, public, criterion)
                filled_assessments.add_row((user, criterion, entity), dict(assessment) | { 
                    "assessment": a,
                    "assessment_min": a_min, 
                    "assessment_max": a_max, 
                })
        return filled_assessments
        
    def sample(self, 
        assessment: Assessment, 
        user: User, 
        entity: Entity, 
        public: bool, 
        criterion: str
    ) -> tuple[float, float, float]:
        """ Returns assessment min, max and value """
        return np.random.random(), 0, 1
