from typing import Mapping

import pandas as pd
import numpy as np

from .base import Scaling

from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import ScoringModel, ScaledScoringModel
from solidago.voting_rights import VotingRights
from solidago.primitives import qr_quantile


class QuantileShift(Scaling):
    def __init__(self,
        quantile: float = 0.15,
        target_score: float = 0.0,
        lipschitz: float = 0.1,
        error: float = 1e-5,
    ):
        """ The scores are shifted so that their quantile zero_quantile equals zero

        Parameters
        ----------
        zero_quantile: float
        """
        self.quantile = quantile
        self.target_score = target_score
        self.lipschitz = lipschitz
        self.error = error

    def main(self, entities: Entities, user_models: UserModels) -> UserModels:
        """ Returns scaled user models
        
        Returns
        -------
        out[user]: ScoringModel
            Will be scaled by the Scaling method
        """
        values, criteria = dict(), set()
        for username, model in user_models:
            for entity in entities:
                multiscore = model(entity)
                for criterion, score in multiscore:
                    if criterion not in values:
                        values[criterion] = list()
                        criteria.add(criterion)
                    values[criterion].append(score.to_triplet())
        
        for criterion in criteria:
            scores, lefts, rights = zip(*values[criterion])
            shift = - qr_quantile(
                lipschitz=self.lipschitz,
                quantile=self.quantile,
                values=np.array(scores),
                voting_rights=np.array([1/len(entities)] * len(entities)),
                left_uncertainties=np.array(lefts),
                right_uncertainties=np.array(rights),
                error=self.error,
            ) + self.target_score

        return UserModels({
            user: ScaledScoringModel(user_model, translation=shift)
            for (user, user_model) in user_models.items()
        })


class QuantileZeroShift(QuantileShift):
    def __init__(
        self,
        zero_quantile: float = 0.15,
        lipschitz: float = 0.1,
        error: float = 0.00001
    ):
        super().__init__(zero_quantile, target_score=0.0, lipschitz=lipschitz, error=error)

    def to_json(self):
        return type(self).__name__, dict(
            zero_quantile=self.quantile,
            lipschitz=self.lipschitz,
            error=self.error
        )
