import numpy as np

from solidago.state import *


class AssessmentGenerator:
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        criteria: Criteria,
        made_public: MadePublic, 
        judgments: Judgments
    ) -> AssessmentsDictionary:
        """ Fills in the assessments """
        for username, criterion_id, assessments in judgments.assessments:
            for index, assessment in assessments.iterrows():
                user = users.get(username)
                entity = entities.get(assessment["entity_id"])
                assessment_min, assessment_max, assessment_value = self.sample(
                    user=user,
                    entity=entity,
                    criterion=criteria.get(criterion_id), 
                    public=made_public[user, entity]
                )
                assessments.loc[index, "assessment_min"] = assessment_min
                assessments.loc[index, "assessment_max"] = assessment_max
                assessments.loc[index, "assessment"] = assessment_value
        return judgments.assessments
        
    def sample(self, user: User, entity: Entity, criterion: Criterion, public: bool) -> tuple[float, float, float]:
        """ Returns assessment min, max and value """
        return 0, 1, np.random.random()

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )
