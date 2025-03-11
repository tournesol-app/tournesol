from typing import Mapping

import numpy as np
import timeit
import logging
logger = logging.getLogger(__name__)

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
        scales = MultiScore(key_names=["depth", "kind", "criterion"])
        for criterion in user_models.criteria():
            logger.info(f"Lipschitz Quantile Shift for criterion={criterion}")
            start = timeit.default_timer()
            scores = user_models(entities, criterion) # key_names == ["username", "entity_name"]
            end = timeit.default_timer()
            logger.info(f"    Computed all user scores in {int(end - start)} seconds for criterion={criterion}")
            start = end
            weights = 1 / scores.groupby("username").transform("size")
            end = timeit.default_timer()
            logger.info(f"    Computed weights in {int(end - start)} seconds for criterion={criterion}")
            start = end
            translation_value = - qr_quantile(
                lipschitz=self.lipschitz,
                quantile=self.quantile,
                values=np.array(scores["value"], dtype=np.float64),
                voting_rights=np.array(weights, dtype=np.float64),
                left_uncertainties=np.array(scores["left_unc"], dtype=np.float64),
                right_uncertainties=np.array(scores["right_unc"], dtype=np.float64),
                error=self.error,
            ) + self.target_score
            end = timeit.default_timer()
            logger.info(f"    Computed shift in {int(end - start)} seconds for criterion={criterion}")
            scales.set(0, "translation", criterion, translation_value, 0, 0)
        return user_models.scale(scales, note="lipschitz_quantile_shift")


class LipschitzQuantileZeroShift(LipschitzQuantileShift):
    def __init__(self,
        zero_quantile: float = 0.15,
        lipschitz: float = 0.1,
        error: float = 0.00001
    ):
        super().__init__(zero_quantile, target_score=0.0, lipschitz=lipschitz, error=error)

