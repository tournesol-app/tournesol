import numpy as np

from solidago.state import *


class AssessmentGenerator:
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        criteria: Criteria,
        made_public: MadePublic, 
        assessments: Assessments
    ) -> Assessments:
        """ Fills in the assessments """
        for (username, entity_name, criterion_name), _ in assessments:
            user = users.get(username)
            entity = entities.get(entity_name)
            criterion = criteria.get(criterion_name)
            public=made_public[user, entity]
            a_min, a_max, a = self.sample(user, entity, criterion, public)
            assessments[user, entity, criterion] |= { "assessment_min": a_min, "assessment_max": a_max, "assessment": a }
        return assessments
        
    def sample(self, user: User, entity: Entity, criterion: Criterion, public: bool) -> tuple[float, float, float]:
        """ Returns assessment min, max and value """
        return 0, 1, np.random.random()

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )
