import pandas as pd

from solidago._state import *
from solidago._pipeline.base import StateFunction


class Average(StateFunction):
    
    def __call__(self, 
        entities: Entities,
        voting_rights: VotingRights,
        user_models: UserModels,
    ) -> ScoringModel:
        """ Returns weighted average of user's scores """
        global_model = DirectScoringModel()
        voting_rights = voting_rights.reorder_keys(["username", "entity_name", "criterion"])
        
        for entity in entities:
        
            total_voting_rights, total_scores = dict(), dict()
            total_lefts, total_rights = dict(), dict()
        
            for user, model in user_models:
                multiscore = model(entity)
        
                for criterion, score in multiscore:
        
                    if score.isnan():
                        continue
        
                    for d in (total_voting_rights, total_scores, total_lefts, total_rights):
                        if criterion not in d:
                            d[criterion] = 0
        
                    total_voting_rights[criterion] += voting_rights[user, entity, criterion]
                    total_scores[criterion] = voting_rights[user, entity, criterion] * output[0]
                    total_lefts[criterion]  = voting_rights[user, entity, criterion] * output[1]
                    total_rights[criterion] = voting_rights[user, entity, criterion] * output[2]
        
            for criterion in total_voting_rights:
                
                if total_voting_rights[criterion] == 0:
                    continue
                
                global_model[entity, criterion] = (
                    total_scores[criterion] / total_voting_rights[criterion],
                    total_lefts[criterion]  / total_voting_rights[criterion],
                    total_rights[criterion] / total_voting_rights[criterion],
                )
        
        return global_model
        
