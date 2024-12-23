import numpy as np

from solidago.state import User, Users, Entity, Entities, Privacy, Assessments, Judgments


class AssessmentGenerator:
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        privacy: Privacy, 
        judgments: Judgments
    ) -> Assessments:
        """ Fills in the assessments """
        for index, assessment in judgments.assessments.iterrows():
            user = users.get(assessment["username"])
            entity = entities.get(assessment["entity_id"])
            private = privacy[user, entity]
            assessment_min, assessment_max, assessment_value = self.sample(user, entity, private)
            judgments.assessments.loc[index, "assessment_min"] = assessment_min
            judgments.assessments.loc[index, "assessment_max"] = assessment_max
            judgments.assessments.loc[index, "assessment"] = assessment_value
        return judgments.assessments
        
    def sample(self, user: User, entity: Entity, private: bool) -> tuple[float, float, float]:
        """ Returns assessment min, max and value """
        return 0, 1, np.random.random()

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )
