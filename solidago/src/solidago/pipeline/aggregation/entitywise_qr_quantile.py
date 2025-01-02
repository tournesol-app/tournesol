import pandas as pd
import numpy as np

from .base import Aggregation

from solidago.state import *
from solidago.primitives.lipschitz import qr_quantile, qr_uncertainty


class EntitywiseQrQuantile(Aggregation):
    def __init__(self, quantile=0.2, lipschitz=0.1, error=1e-5):
        """ Standardize scores so that only a fraction 1 - dev_quantile
        of the scores is further than 1 away from the median,
        and then run qr_median to aggregate the scores.
        
        Parameters
        ----------
        qtl_std_dev: float
        lipschitz: float
        error: float
        """
        self.quantile = quantile
        self.lipschitz = lipschitz
        self.error = error
 
    def main(self, 
        entities: Entities,
        voting_rights: VotingRights,
        user_models: UserModels,
    ) -> ScoringModel:
        """ Returns scaled user models """
        global_scores = DirectScoringModel()
        
        voting_rights = voting_rights.reorder_keys(["entity_name", "username", "criterion"])
        for entity in entities:
            all_scores = self.get_scores(entity, user_models)
            rights = self.get_voting_rights(entity, voting_rights, user_models)
            for criterion, scores_list in all_scores.items():
                if criterion not in rights:
                    continue
                scores, left_uncs, right_uncs = [ np.array(l) for l in zip(*scores_list)) ]
                score = qr_quantile(
                    lipschitz=self.lipschitz,
                    quantile=self.quantile,
                    values=scores,
                    voting_rights=np.array(rights[criterion]),
                    left_uncertainties=left_uncs,
                    right_uncertainties=right_uncs,
                    error=self.error
                )
                uncertainty = qr_uncertainty(
                    lipschitz=self.lipschitz, 
                    values=np.array(dfe["scores"]), 
                    voting_rights=np.array(dfe["voting_rights"]), 
                    left_uncertainties=np.array(dfe["left_uncertainties"]),
                    right_uncertainties=np.array(dfe["right_uncertainties"]),
                    default_dev=1.0,
                    error=self.error,
                    median = score if self.quantile == 0.5 else None,
                )
                global_scores[entity, criterion] = score, uncertainty, uncertainty
                
        return global_scores
    
    def get_scores(self, 
        entity: Entity,
        user_models: UserModels,
    ) -> dict[str, list[MultiScore]]:
        """ Collect all user's multiscores of entity """
        scores = dict()
        for _, model in user_models:
            multiscore = model(entity)
            for criterion, score in multiscore:
                if criterion not in scores:
                    scores[criterion] = list()
                scores[criterion].append(score.to_triplet())
        return scores
        
    def get_voting_rights(self,
        entity: Entity,
        voting_rights: VotingRights,
        user_models: UserModels
    ) -> dict[str, list[float]]:
        result = dict()
        voting_rights = voting_rights.reorder_keys(["entity_name", "username", "criterion"])
        for username, _ in user_models:
            for criterion, value in voting_rights[entity, username]:
                if criterion not in result:
                    result[criterion] = list()
                result[criterion].append(value)
        return result
