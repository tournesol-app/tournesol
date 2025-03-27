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
        scales = MultiScore(key_names=["kind", "criterion"])
        for criterion in user_models.criteria():
            logger.info(f"Lipschitz Quantile Shift for criterion={criterion}")
            start = timeit.default_timer()
            scores = user_models(entities, criterion) # keynames == ["username", "entity_name"]
            end = timeit.default_timer()
            logger.info(f"    Computed all user scores in {int(end - start)} seconds for criterion={criterion}")
            start = end
            n_scored_entities = { username: len(s) for (username,), s in scores.iter("username") }
            values, voting_rights = np.zeros(len(scores)), np.zeros(len(scores))
            lefts, rights = np.zeros(len(scores)), np.zeros(len(scores))
            for index, ((username, entity_name), score) in enumerate(scores):
                values[index], lefts[index], rights[index] = score.to_triplet()
                voting_rights[index] = 1. / n_scored_entities[username]
            end = timeit.default_timer()
            logger.info(f"    Computed weights in {int(end - start)} seconds for criterion={criterion}")
            start = end
            translation_value = - qr_quantile(
                lipschitz=self.lipschitz,
                quantile=self.quantile,
                values=values,
                voting_rights=voting_rights,
                left_uncertainties=lefts,
                right_uncertainties=rights,
                error=self.error,
            ) + self.target_score
            end = timeit.default_timer()
            logger.info(f"    Computed shift in {int(end - start)} seconds for criterion={criterion}")
            scales["translation", criterion] = Score(translation_value, 0, 0)
        return user_models.scale(scales, note="lipschitz_quantile_shift")


class LipschitzQuantileZeroShift(LipschitzQuantileShift):
    def __init__(self,
        zero_quantile: float = 0.15,
        lipschitz: float = 0.1,
        error: float = 0.00001
    ):
        super().__init__(zero_quantile, target_score=0.0, lipschitz=lipschitz, error=error)

