from typing import Union, TYPE_CHECKING

from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction

if TYPE_CHECKING:
    from solidago.generators.ratings import Rate

class Independent(PollFunction):
    """ Fills in Ratings """

    def __init__(self, 
        honest: Union["Rate", list, tuple] | None = None, 
        malicious: Union["Rate", list, tuple] | None = None,
    ):
        import solidago, solidago.generators.ratings as ratings_module
        from solidago.generators.ratings import Deterministic, Negate
        self.honest = solidago.load(honest, ratings_module) if honest else Deterministic()
        self.malicious = solidago.load(malicious, ratings_module, honest=honest) if malicious else Negate(self.honest)
        
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        public_settings: PublicSettings, 
        ratings: Ratings
    ) -> Ratings:
        """ Fills in the ratings """
        result = Ratings()
        for index, rating in enumerate(ratings):
            user, entity = users[rating["username"]], entities[rating["entity_name"]]
            public = public_settings.get(username=user.name, entity_name=entity.name)["public"]
            assert isinstance(user, User) and isinstance(entity, Entity)
            self.rate(rating, user, entity, public, rating["criterion"])
        return result
    
    def rate(self, rating: Rating, user: User, entity: Entity, public: bool, criterion: str):
        malicious = "is_trustworthy" in user and not user["is_trustworthy"]
        sample_function = self.malicious if malicious else self.honest
        sample_function(rating, user, entity, public, criterion)


