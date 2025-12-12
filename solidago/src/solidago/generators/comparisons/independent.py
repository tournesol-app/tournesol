from typing import Union, TYPE_CHECKING

from solidago.poll import *
from solidago.generators.generator import GeneratorStep

if TYPE_CHECKING:
    from solidago.generators.comparisons import Compare

class Independent(GeneratorStep):
    """ Fills in the comparisons """
    
    def __init__(self, 
        honest: Union["Compare", list, tuple] | None = None, 
        malicious: Union["Compare", list, tuple] | None = None,
    ):
        from solidago.generators.comparisons import Compare, Deterministic, Negate
        self.honest = Compare.load(honest) if honest else Deterministic()
        self.malicious = Compare.load(malicious, honest=honest) if malicious else Negate(honest)
        
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        made_public: MadePublic, 
        comparisons: Comparisons
    ) -> Comparisons:
        result = Comparisons()
        for (username, criterion, left_name, right_name), comparison in comparisons:
            user, left, right = users[username], entities[left_name], entities[right_name]
            left_public, right_public = made_public[user, left], made_public[user, right]
            comparison = self.compare(comparison, user, left, right, left_public, right_public, criterion)
            result[username, criterion, left_name, right_name] = comparison
        return result
    
    def compare(self, 
        comparison: Comparison, 
        user: User, left: Entity, right: Entity, 
        left_public: bool, right_public, 
        criterion: str
    ) -> Comparison:
        malicious = "is_trustworthy" in user and not user.is_trustworthy
        sample_function = self.malicious if malicious else self.honest
        return sample_function(comparison, user, left, right, left_public, right_public, criterion)


