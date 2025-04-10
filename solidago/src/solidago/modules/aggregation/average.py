import pandas as pd

from solidago.state import *
from solidago.modules.base import StateFunction


class Average(StateFunction):
    
    def __call__(self, 
        entities: Entities,
        voting_rights: VotingRights,
        user_models: UserModels,
        *args, **kwargs,
    ) -> ScoringModel:
        """ Returns weighted average of user's scores """
        super().__init__(*args, **kwargs)
        global_model = DirectScoring(note="average")
        multiscores = user_models(entities)

        for (entity_name, criterion), scores in multiscores.iter("entity_name", "criterion"):
            v = voting_rights.get(entity_name=entity_name, criterion=criterion)
            weighted_sum = sum([score * v[username] for username, score in scores], Score(0, 0, 0))
            sum_of_weights = sum([v[username] for username, _ in scores])
            global_model[entity_name, criterion] = weighted_sum / sum_of_weights
        
        return global_model
        
