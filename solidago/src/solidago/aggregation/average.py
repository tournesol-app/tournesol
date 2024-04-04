import pandas as pd

from solidago.voting_rights import VotingRights
from solidago.scoring_model import ScoringModel, DirectScoringModel

from .base import Aggregation


class Average(Aggregation):
    def __call__(
        self, 
        voting_rights: VotingRights,
        user_models: dict[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame
    ) -> tuple[dict[int, ScoringModel], ScoringModel]:
        """ Returns scaled user models
        
        Parameters
        ----------
        voting_rights: VotingRights
            voting_rights[user, entity]: float
        user_models: dict[int, ScoringModel]
            user_models[user] is user's scoring model
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        entities: DataFrame with columns
            * entity_id (int, ind)

        Returns
        -------
        updated_user_models[user]: ScoringModel
            Returns a scaled user model
        global_model: ScoringModel
            Returns a global scoring model
        """
        global_model = DirectScoringModel()
        
        for entity in entities.index:
        
            total_voting_rights, total_scores = 0, 0
            total_lefts, total_rights = 0, 0
        
            for user in user_models:
                output = user_models[user](entity, entities.loc[entity])
                if output is None:
                    continue
                total_voting_rights += voting_rights[user, entity]
                total_scores = voting_rights[user, entity] * output[0]
                total_lefts  = voting_rights[user, entity] * output[1]
                total_rights = voting_rights[user, entity] * output[2]
        
            if total_voting_rights == 0:
                continue
        
            score = total_scores / total_voting_rights
            left  = total_lefts  / total_voting_rights
            right = total_rights / total_voting_rights
            global_model[entity] = score, left, right
        
        return user_models, global_model
        
