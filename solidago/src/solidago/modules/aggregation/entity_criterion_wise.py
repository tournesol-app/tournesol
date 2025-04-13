from abc import abstractmethod
from concurrent.futures import ProcessPoolExecutor, as_completed

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
        scores = user_models(entities).reorder("criterion", "entity_name", "username")
        kwargs = {c: (entities, voting_rights[c], scores[c]) for c in user_models.criteria()}
        with ProcessPoolExecutor(max_workers=self.max_workers) as e:
            futures = {e.submit(self.aggregate_criterion, *args): c for c, args in kwargs.items()}
            for f in as_completed(futures):
                criterion = futures[f]
                for entity_name, score in f.result().items():
                    global_model[entity_name, criterion] = score

        return global_model
    
    def aggregate_criterion(self, 
        entities: Entities, 
        voting_rights: VotingRights, # keynames == ["entity_name", "username"]
        scores: MultiScore, # keynames == ["entity_name", "username"]
    ) -> dict[str, Score]:
        return {e.name: self.aggregate(scores[e], voting_rights[e]) for e in entities}
        
    @abstractmethod
    def aggregate(self, 
        scores: MultiScore, # keynames == "username"
        voting_rights: VotingRights, # keynames == "username"
    ) -> Score:
        raise NotImplemented
