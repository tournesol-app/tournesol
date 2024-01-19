import numpy as np
import pandas as pd

from . import Scaling

from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import ScoringModel


class Mehestan(Scaling):
    def __init__(self, lipschitz=0.1, min_n_judged_entities=10, n_scalers_max=1000, error=1e-5):
        """ Mehestan performs Lipschitz-resilient ollaborative scaling.
        See "Robust Sparse Voting", Youssef Allouah, Rachid Guerraoui, Lȩ Nguyên Hoang
        and Oscar Villemaud, published at AISTATS 2024.
        
        Parameters
        ----------
        lipschitz: float
            Resilience parameters. Larger values are more resilient, but less accurate.
        min_n_comparison: float
            Minimal number of comparisons to be a potential scaling-calibration user
        n_scalers_max: int
            Maximal number of scaling-calibration users
        error: float
            Error bound
        """
        self.lipschitz = lipschitz
        self.min_n_judged_entities = min_n_judged_entities
        self.n_scalers_max = n_scalers_max
        self.error = error
    
    def compute_n_judged_entities(self, user_models, users, entities, voting_rights):
        results = np.zeros(len(users))
        for user in user_models:
            scored_entities = user_models.scored_entities(entities)
            for entity in scored_entities:
                output = user_models[user](entity, entities.loc[entity])
                if output is not None:
                    results[user] += voting_rights[user, entity]        
        return results
    
    def compute_scalers(self, n_judged_entities):
        argsort = np.argsort(n_judged_entities)
        is_scaler = np.array([False] * len(n_judged_entities))
        for user in range(min(self.n_scalers_max, len(n_judged_entities))):
            if n_judged_entities[argsort[-user]] < self.min_n_judged_entities:
                break
            is_scaler[argsort[-user]] = True
        return is_scaler
    
    def compute_score_diffs(self, user_models, users, entities):
        score_diffs = list()
        for user in user_models:
            score_diffs.append(dict())
            scored_entities = user_models.scored_entities(entities)
            for index, a in enumerate(scored_entities):
                for b in scored_entities[index + 1:]:
                    score_a, left_a, right_a = user_models[user](a, entities.loc[a])
                    score_b, left_b, right_b = user_models[user](b, entities.loc[b])
                    if score_a - score_b >= left_a + right_b:
                        if a not in score_diffs[user]:
                            score_diffs[user][a] = dict()
                        score_diffs[user][a][b] = (
                            score_a - score_b, 
                            score_a - score_b - left_a - right_b,
                            score_a - score_b + right_a + left_b
                        )
                    if score_b - score_a >= left_b + right_a:
                        if a not in score_diffs[user]:
                            score_diffs[user][a] = dict()
                        score_diffs[user][a][b] = (
                            score_b - score_a, 
                            score_b - score_a - left_b - right_a,
                            score_b - score_a + right_b + left_a
                        )
        return score_diffs                    
    
    def scale_scalers(self, user_models, scalers, entities, voting_rights, score_diffs):
        scaled_models = dict()
        raise NotImplementedError
        return scaled_models
        
    def scale_non_scalers(self, user_models, non_scalers, entities, 
            voting_rights, scalers, scaled_models, pairs):
        scaled_models = dict()
        raise NotImplementedError
        return scaled_models
    
    def __call__(
        self, 
        user_models: dict[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame,
        voting_rights: VotingRights,
        privacy: PrivacySettings
    ) -> dict[int, ScoringModel]:
        """ Returns scaled user models
        
        Parameters
        ----------
        user_models: dict[int, ScoringModel]
            user_models[user] is user's scoring model
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        entities: DataFrame with columns
            * entity_id (int, ind)
        voting_rights: VotingRights
            voting_rights[user, entity]: float
        privacy: PrivacySettings
            privacy[user, entity] in { True, False, None }

        Returns
        -------
        out[user]: ScoringModel
            Will be scaled by the Scaling method
        """
        n_judged_entities = self.compute_n_judged_entities(user_models, 
            users, entities, voting_rights)
        users.assign(is_scaler=self.compute_scalers(n_judged_entities))
        scalers = users[users["is_scaler"]]
        non_scalers = users[not users["is_scaler"]]
        
        score_diffs = self.compute_score_diffs(user_models, users, entities)
        
        scaled_models = scale_scalers(user_models, scalers, entities, voting_rights, pairs)
        scaled_models = scale_non_scalers(user_models, non_scalers, entities, 
            voting_rights, scalers, scaled_models, pairs)
        
        return scaled_models

