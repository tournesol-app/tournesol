from solidago.state import Users, Entities, VotingRights, Judgments


class EngagementGenerator:
    
    def __call__(self, users: Users, entities: Entities) -> tuple[VotingRights, Judgments]:
        """ Defines how users engage with entities, including in terms of private/public engagement """
        return VotingRights(), Judgments()

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )

                
