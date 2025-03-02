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
        multiscores = user_models(entities)
        voting_rights = voting_rights.groupby(["entity_name", "criterion"])

        for (entity_name, criterion), scores in multiscores.groupby(["entity_name", "criterion"]):
            weighted_sum = sum([
                score * voting_rights[entity_name, criterion].get(username)
                for username, score in scores
            ], Score(0, 0, 0))
            sum_of_weights = voting_rights[entity_name, criterion]["voting_right"].sum()
            global_model.set(entity_name, criterion, weighted_sum / sum_of_weights)
        
        return global_model
        
