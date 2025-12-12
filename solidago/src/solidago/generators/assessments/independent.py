from typing import Union, TYPE_CHECKING

from solidago.poll import *
from solidago.generators.generator import GeneratorStep

if TYPE_CHECKING:
    from solidago.generators.assessments import Assess

class Independent(GeneratorStep):
    """ Fills in Assessments """

    def __init__(self, 
        honest: Union["Assess", list, tuple] | None = None, 
        malicious: Union["Assess", list, tuple] | None = None,
    ):
        from solidago.generators.assessments import Assess, Deterministic, Negate
        self.honest = Assess.load(honest) if honest else Deterministic()
        self.malicious = Assess.load(malicious, honest=honest) if malicious else Negate(honest)
        
    def __call__(self, 
        users: Users, 
        entities: Entities, 
        made_public: MadePublic, 
        assessments: Assessments
    ) -> Assessments:
        """ Fills in the assessments """
        result = Assessments()
        for (username, criterion, entity_name), assessment in assessments:
            user, entity = users[username], entities[entity_name]
            assessment = self.assess(assessment, user, entity, made_public[user, entity], criterion)
            result[username, criterion, entity_name] = assessment
        return result
    
    def assess(self, assessment: Assessment, user: User, entity: Entity, public: bool, criterion: str) -> Assessment:
        malicious = "is_trustworthy" in user and not user.is_trustworthy
        sample_function = self.malicious if malicious else self.honest
        return sample_function(assessment, user, entity, public, criterion)


