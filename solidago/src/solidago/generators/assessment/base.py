import numpy as np

from solidago.state import *
from solidago.modules import StateFunction


class AssessmentGen(StateFunction):
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        made_public: MadePublic, 
        assessments: Assessments
    ) -> Assessments:
        """ Fills in the assessments """
        result = Assessments()
        for (username, criterion, entity_name), assessment in assessments:
            user, entity = users[username], entities[entity_name]
            assessment = self.sample(assessment, user, entity, made_public[user, entity], criterion)
            result[username, criterion, entity_name] = assessment
        return result
        
    def sample(self, 
        assessment: Assessment, 
        user: User, 
        entity: Entity, 
        public: bool, 
        criterion: str
    ) -> Assessment:
        return Assessment(np.random.random(), 0, 1)
