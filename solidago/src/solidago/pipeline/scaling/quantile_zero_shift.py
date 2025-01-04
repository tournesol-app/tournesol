from typing import Mapping

import pandas as pd
import numpy as np

from solidago.primitives import qr_quantile
from solidago.state import *
from solidago.pipeline.base import StateFunction


class QuantileShift(StateFunction):
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
        scores = user_models.score(entities).reorder_keys(["criterion"])
        translation2scale = lambda translation: (1, 0, 0, translation, 0, 0)
        scalings = dict()
        for criterion in scores.get_set("criterion"):
            scores_df = scores[criterion].to_df()
            score_values = scores_df["score"]
            left_uncertainties = scores_df["left_unc"]
            right_uncertainties = scores_df["right_unc"]
            translation_value = - qr_quantile(
                lipschitz=self.lipschitz,
                quantile=self.quantile,
                values=np.array(score_values),
                voting_rights=np.array([1/len(entities)] * len(entities)),
                left_uncertainties=np.array(left_uncertainties),
                right_uncertainties=np.array(right_uncertainties),
                error=self.error,
            ) + self.target_score
            scalings[criterion] = translation_value2scale(translation_value)

        return UserModels({
            username: MultiScaledModel(model, scalings)
            for username, model in user_models
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
