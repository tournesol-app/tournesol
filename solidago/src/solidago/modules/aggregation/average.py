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
        multiscores = user_models(entities).reorder_keys(["entity_name", "criterion", "username"])
        voting_rights = voting_rights.groupby(["entity_name", "criterion"])

        for entity_name in multiscores.get_set("entity_name"):
            for criterion in multiscores[entity_name].get_set("criterion"):
                
                weighted_sum = sum([
                    score * voting_rights[entity_name, criterion].get(username)
                    for username, score in multiscores[entity_name, criterion]
                ], Score(0, 0, 0))
                sum_of_weights = voting_rights[entity_name, criterion]["voting_right"].sum()
                global_model[entity_name, criterion] = weighted_sum / sum_of_weights
        
        return global_model
        
