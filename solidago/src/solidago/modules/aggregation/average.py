from solidago.state import *
from solidago.modules.aggregation.entity_criterion_wise import EntityCriterionWise


class Average(EntityCriterionWise):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def aggregate(self, 
        user_models: UserModels, 
        voting_rights: VotingRights, # keynames == "username"
        criterion: str,
        entity: Entity, 
    ) -> float:
        scores = user_models(entity, criterion)
        if len(scores) == 0:
            return Score.nan()
        weighted_sum = sum([score * voting_rights[u] for (u,), score in scores], Score(0, 0, 0))
        sum_of_weights = sum([voting_rights[username] for (username,), _ in scores])
        return weighted_sum / sum_of_weights
        
        
