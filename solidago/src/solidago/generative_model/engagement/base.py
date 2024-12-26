from solidago.state import Users, Entities, Criteria, MadePublic, Judgments


class EngagementGenerator:
    
    def __call__(self, users: Users, entities: Entities, criteria: Criteria) -> tuple[MadePublic, Judgments]:
        """ Defines how users engage with entities, including in terms of private/public engagement """
        return MadePublic(), Judgments()

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )

                
