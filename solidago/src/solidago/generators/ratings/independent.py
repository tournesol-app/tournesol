from typing import Union, TYPE_CHECKING

from solidago.poll import *
from solidago.generators.generator import GeneratorStep

if TYPE_CHECKING:
    from solidago.generators.ratings import Rate

class Independent(GeneratorStep):
    """ Fills in Ratings """

    def __init__(self, 
        honest: Union["Rate", list, tuple] | None = None, 
        malicious: Union["Rate", list, tuple] | None = None,
    ):
        from solidago.generators.ratings import Rate, Deterministic, Negate
        self.honest = Rate.load(honest) if honest else Deterministic()
        self.malicious = Rate.load(malicious, honest=honest) if malicious else Negate(honest)
        
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        made_public: MadePublic, 
        ratings: Ratings
    ) -> Ratings:
        """ Fills in the ratings """
        result = Ratings()
        for (username, criterion, entity_name), rating in ratings:
            user, entity = users[username], entities[entity_name]
            rating = self.rate(rating, user, entity, made_public[user, entity], criterion)
            result[username, criterion, entity_name] = rating
        return result
    
    def rate(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str) -> Rating:
        malicious = "is_trustworthy" in user and not user.is_trustworthy
        sample_function = self.malicious if malicious else self.honest
        return sample_function(rating, user, entity, public, criterion)


