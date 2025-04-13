from abc import abstractmethod

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
        args = entities, voting_rights, user_models
        
        if self.max_workers == 1:
            for (entity_name, score), score in self.batch(0, *args):
                global_model[entity_name, criterion] = score
            return global_model
        
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=self.max_workers) as e:
            futures = {e.submit(self.batch, i, *args) for i in range(self.max_workers)}
            for f in as_completed(futures):
                for (entity_name, criterion), score in f.result().items():
                    global_model[entity_name, criterion] = score
        return global_model
    
    def batch(self, 
        batch_number: int,
        entities: Entities, 
        voting_rights: VotingRights, # keynames == ["entity_name", "username"]
        user_models: UserModels, # keynames == ["entity_name", "username"]
    ) -> dict[tuple[str, str], Score]:
        indices = range(batch_number, len(entities), self.max_workers)
        batch_entities = {entities.get_by_index(i) for i in indices}
        return {
            (e.name, c): self.aggregate(user_models(e, c), voting_rights[e, c]) 
            for e in batch_entities
            for c in user_models.criteria()
        }
        
    @abstractmethod
    def aggregate(self, 
        scores: MultiScore, # keynames == "username"
        voting_rights: VotingRights, # keynames == "username"
    ) -> Score:
        raise NotImplemented
