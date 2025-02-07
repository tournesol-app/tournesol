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
            assessment = self.sample(
                assessment=assessment, 
                user=users.get(username), 
                entity=entities.get(entity_name), 
                public=made_public.get(username, entity_name),
                criterion=criterion
            )
            result.add_row(username, criterion, entity_name, assessment)
        return result
        
    def sample(self, 
        assessment: Assessment, 
        user: User, 
        entity: Entity, 
        public: bool, 
        criterion: str
    ) -> Assessment:
        assessment["value"] = np.random.random()
        assessment["min"] = 0
        assessment["max"] = 1
        return assessment
