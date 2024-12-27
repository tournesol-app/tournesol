from solidago.state import *


class EngagementGenerator:
    
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        criteria: Criteria
    ) -> tuple[MadePublic, Assessments, Comparisons]:
        """ Defines how users engage with entities, including in terms of private/public engagement """
        return MadePublic(), Assessments(), Comparisons()

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )

                
