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
        voting_rights = voting_rights.reorder("entity_name", "criterion", "username")
        args_list = [
            (user_models, entity, criterion, voting_rights[entity, criterion]) 
            for entity in entities 
            for criterion in user_models.criteria()
        ]
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as e:
            futures = [e.submit(self.aggregate, *args) for args in args_list]
            for (_, entity, criterion, _), future in zip(args_list, as_completed(futures)):
                global_model[entity, criterion] = future.result()

        return global_model
    
    @abstractmethod
    def aggregate(self, 
        user_models: UserModels, 
        entity: Entity, 
        criterion: str,
        voting_rights: VotingRights, # keynames == "username"
    ) -> float:
        raise NotImplemented
