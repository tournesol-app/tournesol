from abc import abstractmethod
from concurrent.futures import ThreadPoolExecutor, as_completed

from solidago.state import *
from solidago.modules.base import StateFunction


class EntityCriterionWise(StateFunction):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)       
    
    def __call__(self, 
        entities: Entities,
        voting_rights: VotingRights,
        user_models: UserModels,
        *args, **kwargs,
    ) -> ScoringModel:
        """ Returns weighted average of user's scores """
        global_model = DirectScoring(note="average")
        voting_rights = voting_rights.reorder("criterion", "entity_name", "username")
        
        def aggregate(criterion):
            return {
                str(entity): self.aggregate(user_models, voting_rights[criterion, entity], criterion, entity) 
                for entity in entities
            }
        with ThreadPoolExecutor(max_workers=self.max_workers) as e:
            futures = {e.submit(aggregate, c): c for c in user_models.criteria()}
            for f in as_completed(futures):
                criterion = futures[f]
                for entity_name, score in f.result().items():
                    global_model[entity_name, criterion] = score

        return global_model
    
    @abstractmethod
    def aggregate(self, 
        user_models: UserModels, 
        voting_rights: VotingRights, # keynames == "username"
        criterion: str,
        entity: Entity, 
    ) -> float:
        raise NotImplemented
