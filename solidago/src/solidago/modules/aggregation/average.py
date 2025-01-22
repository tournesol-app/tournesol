import pandas as pd

from solidago.state import *
from solidago.modules.base import StateFunction


class Average(StateFunction):
    
    def __call__(self, 
        entities: Entities,
        voting_rights: VotingRights,
        user_models: UserModels,
    ) -> ScoringModel:
        """ Returns weighted average of user's scores """
        global_model = DirectScoring()
        voting_rights = voting_rights.reorder_keys(["entity_name", "criterion", "username"])
        multiscores = user_models(entities).reorder_keys(["entity_name", "criterion", "username"])

        for entity_name in multiscores.get_set("entity_name"):
            for criterion in multiscores[entity_name].get_set("criterion"):
                
                weights = voting_rights[entity_name, criterion]
                weighted_sum = sum([
                    score * weights[username]
                    for username, score in multiscores[entity_name, criterion]
                ], Score(0, 0, 0))
                sum_of_weights = weights.to_df()["voting_right"].sum()
                global_model[entity_name, criterion] = weighted_sum / sum_of_weights
        
        return global_model
        
