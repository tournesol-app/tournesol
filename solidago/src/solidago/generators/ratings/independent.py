from copy import deepcopy
from typing import Any, Union, TYPE_CHECKING

from solidago.poll import *
from solidago.functions.poll_function import PollFunction

if TYPE_CHECKING:
    from solidago.generators.ratings import Rate

class Independent(PollFunction):
    """ Fills in Ratings """

    def __init__(self, 
        honest: Union["Rate", list, tuple] | None = None, 
        malicious: Union["Rate", list, tuple] | None = None,
    ):
        import solidago, solidago.generators.ratings as m
        self.honest = solidago.load(honest, m, m.Rate, m.Deterministic())
        self.malicious = solidago.load(malicious, m, m.Rate, m.Negate(self.honest))
        
    def fn(self, 
        users: Users, 
        entities: Entities, 
        public_settings: PublicSettings, 
        ratings: Ratings
    ) -> Ratings:
        """ Fills in the ratings """
        result = Ratings()
        for rating in ratings:
            user, entity = users[rating["username"]], entities[rating["entity_name"]]
            public = public_settings.get(username=user.name, entity_name=entity.name)["public"]
            kwargs = self.rate(rating, user, entity, public, rating["criterion"])
            result.append(deepcopy(rating), **kwargs)
        return result
    
    def rate(self, 
        rating: Rating, 
        user: User, entity: Entity, public: bool, criterion: str
    ) -> dict[str, Any]:
        rate = self.honest if user.get("trustworthy", True) else self.malicious
        return rate(rating, user, entity, public, criterion)

