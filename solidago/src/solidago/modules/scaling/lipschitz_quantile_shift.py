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
        n_sampled_entities_per_user: int=100,
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
        self.n_sampled_entities_per_user = n_sampled_entities_per_user

    def __call__(self, entities: Entities, user_models: UserModels) -> UserModels:
        """ Returns scaled user models
        
        Returns
        -------
        out[user]: ScoringModel
            Will be scaled by the Scaling method
        """
        scales = MultiScore(["kind", "criterion"])
        args = entities, user_models

        if self.max_workers == 1:
            for criterion in user_models.criteria():
                scales["translation", criterion] = self.translation(*args, criterion)
            return user_models.scale(scales, note="lipschitz_quantile_shift")

        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=self.max_workers) as e:
            futures = {e.submit(self.translation, *args, c): c for c in user_models.criteria()}
            for f in as_completed(futures):
                criterion = futures[f]
                scales["translation", criterion] = f.result()
        return user_models.scale(scales, note="lipschitz_quantile_shift")

    def translation(self, entities: Entities, user_models: UserModels, criterion: str) -> Score:
        scores = user_models(entities, criterion, self.n_sampled_entities_per_user)
        # scores.keynames == ["username", "entity_name"]
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
        return Score(translation_value, 0, 0)
        
    def save_result(self, state: State, directory: Optional[str]=None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving common scales")
            state.user_models.save_common_scales(directory)
        logger.info("Saving state.json")
        return state.save_instructions(directory)


class LipschitzQuantileZeroShift(LipschitzQuantileShift):
    def __init__(self,
        zero_quantile: float = 0.15,
        lipschitz: float = 0.1,
        error: float = 0.00001
    ):
        super().__init__(zero_quantile, target_score=0.0, lipschitz=lipschitz, error=error)

