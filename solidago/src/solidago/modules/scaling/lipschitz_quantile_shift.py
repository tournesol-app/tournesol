from typing import Optional

import numpy as np
import logging
logger = logging.getLogger(__name__)

from solidago.primitives import qr_quantile
from solidago.primitives.timer import time
from solidago.state import *
from solidago.modules.base import StateFunction


class LipschitzQuantileShift(StateFunction):
    def __init__(self,
        quantile: float = 0.15,
        target_score: float = 0.0,
        lipschitz: float = 0.1,
        error: float = 1e-5,
        *args, **kwargs,
    ):
        """ The scores are shifted so that their quantile zero_quantile equals zero

        Parameters
        ----------
        zero_quantile: float
        """
        super().__init__(*args, **kwargs)
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
        scales = MultiScore(["kind", "criterion"])
        for criterion in user_models.criteria():
            with time(logger, f"Lipschitz Quantile Shift for criterion={criterion}"):
                scores = user_models(entities, criterion) # keynames == ["username", "entity_name"]
                n_scored_entities = { username: len(s) for (username,), s in scores.iter("username") }
                values, voting_rights = np.zeros(len(scores)), np.zeros(len(scores))
                lefts, rights = np.zeros(len(scores)), np.zeros(len(scores))
                for index, ((username, entity_name), score) in enumerate(scores):
                    values[index], lefts[index], rights[index] = score.to_triplet()
                    voting_rights[index] = 1. / n_scored_entities[username]
                translation_value = - qr_quantile(
                    lipschitz=self.lipschitz,
                    quantile=self.quantile,
                    values=values,
                    voting_rights=voting_rights,
                    left_uncertainties=lefts,
                    right_uncertainties=rights,
                    error=self.error,
                ) + self.target_score
                scales["translation", criterion] = Score(translation_value, 0, 0)
        with time(logger, "    Add common scales to user models"):
            scaled_models = user_models.scale(scales, note="lipschitz_quantile_shift")
        return scaled_models

    def save_result(self, state: State, directory: Optional[str]=None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving common scales")
            state.user_models.common_scales.save(directory, "common_scales.csv")
        logger.info("Saving state.json")
        return state.save_instructions(directory)

class LipschitzQuantileZeroShift(LipschitzQuantileShift):
    def __init__(self,
        zero_quantile: float = 0.15,
        lipschitz: float = 0.1,
        error: float = 0.00001
    ):
        super().__init__(zero_quantile, target_score=0.0, lipschitz=lipschitz, error=error)

