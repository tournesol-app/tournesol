from typing import Mapping

import pandas as pd
import numpy as np

from solidago.primitives import qr_quantile
from solidago.state import *
from solidago.modules.base import StateFunction


class LipschitzQuantileShift(StateFunction):
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

    def __call__(self, entities: Entities, user_models: UserModels) -> UserModels:
        """ Returns scaled user models
        
        Returns
        -------
        out[user]: ScoringModel
            Will be scaled by the Scaling method
        """
        scores = user_models.score(entities).reorder_keys(["criterion", "username", "entity_name"])
        scales = ScaleDict(key_names=["criterion"]) # the same scale will apply to all users
        for criterion in scores.get_set("criterion"):
            scores_df = scores[criterion].to_df()
            weights = 1 / scores_df.groupby("username").transform("size")
            translation_value = - qr_quantile(
                lipschitz=self.lipschitz,
                quantile=self.quantile,
                values=np.array(scores_df["score"], dtype=np.float64),
                voting_rights=np.array(weights, dtype=np.float64),
                left_uncertainties=np.array(scores_df["left_unc"], dtype=np.float64),
                right_uncertainties=np.array(scores_df["right_unc"], dtype=np.float64),
                error=self.error,
            ) + self.target_score
            scales[criterion] = (1, 0, 0, translation_value, 0, 0)

        return UserModels({
            username: ScaledModel(model, scales, note="quantile_shift")
            for username, model in user_models
        })


class LipschitzQuantileZeroShift(LipschitzQuantileShift):
    def __init__(self,
        zero_quantile: float = 0.15,
        lipschitz: float = 0.1,
        error: float = 0.00001
    ):
        super().__init__(zero_quantile, target_score=0.0, lipschitz=lipschitz, error=error)

