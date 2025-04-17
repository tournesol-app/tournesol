from abc import abstractmethod

import logging

logger = logging.getLogger(__name__)

from solidago.state import *
from solidago.modules.base import StateFunction
from solidago.primitives.timer import time


class EntityCriterionWise(StateFunction):
    note: str="entity_criterion_wise_aggregation"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __call__(self, 
        entities: Entities,
        voting_rights: VotingRights,
        user_models: UserModels,
        *args, **kwargs,
    ) -> ScoringModel:
        """ Returns weighted average of user's scores """
        global_model = ScoringModel(note=type(self).note)
        voting_rights = voting_rights.reorder("entity_name", "criterion", "username")
        scores = user_models(entities, max_workers=self.max_workers)
        scores = scores.reorder("entity_name", "criterion", "username")
        args = entities, voting_rights, scores, user_models.criteria()
        
        if self.max_workers == 1:
            for (entity_name, criterion), score in self.batch(0, *args).items():
                global_model[entity_name, criterion] = score
            return global_model
        
        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=self.max_workers) as e:
            futures = {e.submit(self.batch, i, *args) for i in range(self.max_workers)}
            results = [f.result() for f in as_completed(futures)]
        for result in results:
            for (entity_name, criterion), score in result.items():
                global_model[entity_name, criterion] = score
        return global_model
    
    def batch(self, 
        batch_number: int,
        entities: Entities, 
        voting_rights: VotingRights, # keynames == ["entity_name", "criterion", "username"]
        scores: MultiScore, # keynames == ["entity_name", "criterion", "username"]
        criteria: list[str],
    ) -> dict[tuple[str, str], Score]:
        indices = range(batch_number, len(entities), self.max_workers)
        batch_entities = {entities.get_by_index(i) for i in indices}
        results = dict()
        for index, e in enumerate(batch_entities):
            for c in criteria:
                results[(e.name, c)] = self.aggregate(scores[e, c], voting_rights[e, c])
        return results
        
    @abstractmethod
    def aggregate(self, 
        scores: MultiScore, # keynames == "username"
        voting_rights: VotingRights, # keynames == "username"
    ) -> Score:
        raise NotImplemented
