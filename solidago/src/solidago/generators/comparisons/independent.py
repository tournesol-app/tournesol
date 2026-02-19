from typing import Union, TYPE_CHECKING

from solidago.poll import *
from solidago.poll_functions.poll_function import PollFunction

if TYPE_CHECKING:
    from solidago.generators.comparisons import Compare


class Independent(PollFunction):
    """ Fills in the comparisons """
    
    def __init__(self, 
        honest: Union["Compare", list, tuple] | None = None, 
        malicious: Union["Compare", list, tuple] | None = None,
    ):
        from solidago.generators.comparisons import Deterministic, Negate
        import solidago, solidago.generators.comparisons as comparisons_module
        self.honest = solidago.load(honest, comparisons_module) if honest else Deterministic()
        self.malicious = solidago.load(malicious, comparisons_module, honest=honest) if malicious else Negate(self.honest)
        
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        public_settings: PublicSettings, 
        comparisons: Comparisons
    ) -> Comparisons:
        result = Comparisons()
        for comparison in comparisons:
            user = users[comparison["username"]], 
            left, right = entities[comparison["left_name"]], entities[comparison["right_name"]]
            assert isinstance(user, User) and isinstance(left, Entity) and isinstance(right, Entity)
            left_public = public_settings.get(username=user.name, entity_name=left.name)["public"]
            right_public = public_settings.get(username=user.name, entity_name=right.name)["public"]
            self.compare(comparison, user, left, right, left_public, right_public, comparison["criterion"])
        return result
    
    def compare(self, 
        comparison: Comparison, 
        user: User, left: Entity, right: Entity, 
        left_public: bool, right_public, 
        criterion: str
    ):
        malicious = "is_trustworthy" in user and not user["is_trustworthy"]
        sample_function = self.malicious if malicious else self.honest
        sample_function(comparison, user, left, right, left_public, right_public, criterion)


