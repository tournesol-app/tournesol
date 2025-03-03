from typing import Mapping

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
        scores = user_models.score(entities) # key_names == ["username", "criterion", "entity_name"]
        scales = MultiScore(key_names=["depth", "kind", "criterion"])
        for criterion, user_scores in scores.to_dict(["criterion"]):
            weights = 1 / user_scores.groupby("username").transform("size")
            translation_value = - qr_quantile(
                lipschitz=self.lipschitz,
                quantile=self.quantile,
                values=np.array(user_scores["value"], dtype=np.float64),
                voting_rights=np.array(weights, dtype=np.float64),
                left_uncertainties=np.array(user_scores["left_unc"], dtype=np.float64),
                right_uncertainties=np.array(user_scores["right_unc"], dtype=np.float64),
                error=self.error,
            ) + self.target_score
            scales.set(0, "translations", criterion, translation_value, 0, 0)
        return user_models.scale(scales, note="lipschitz_quantile_shift")


class LipschitzQuantileZeroShift(LipschitzQuantileShift):
    def __init__(self,
        zero_quantile: float = 0.15,
        lipschitz: float = 0.1,
        error: float = 0.00001
    ):
        super().__init__(zero_quantile, target_score=0.0, lipschitz=lipschitz, error=error)

