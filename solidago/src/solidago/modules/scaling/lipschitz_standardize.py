from typing import Optional
from concurrent.futures import ProcessPoolExecutor, as_completed

import numpy as np
import logging

logger = logging.getLogger(__name__)

from solidago.primitives import qr_standard_deviation
from solidago.primitives.timer import time
from solidago.state import *
from solidago.modules.base import StateFunction


class LipschitzStandardize(StateFunction):
    def __init__(self, dev_quantile: float=0.9, lipschitz: float=0.1, error: float=1e-5, *args, **kwargs):
        """ The scores are shifted so that their quantile zero_quantile equals zero
        
        Parameters
        ----------
        dev_quantile: float
        """
        super().__init__(*args, **kwargs)
        self.dev_quantile = dev_quantile
        self.lipschitz = lipschitz
        self.error = error

    def __call__(self, entities: Entities, user_models: UserModels) -> UserModels:
        scales = MultiScore(["kind", "criterion"])
        args = entities, user_models
        with ProcessPoolExecutor(max_workers=self.max_workers) as e:
            futures = {e.submit(self.multiplier, *args, c): c for c in user_models.criteria()}
            for f in as_completed(futures):
                criterion = futures[f]
                scales["multiplier", criterion] = f.result()
        return user_models.scale(scales, note="lipschitz_standardardize")
    
    def multiplier(self, entities: Entities, user_models: UserModels, criterion: str) -> Score:
        scores = user_models(entities, criterion) # keynames == ["username", "entity_name"]
        n_scored_entities = { username: len(s) for (username,), s in scores.iter("username") }
        values, voting_rights = np.zeros(len(scores)), np.zeros(len(scores))
        lefts, rights = np.zeros(len(scores)), np.zeros(len(scores))
        for index, ((username, entity_name), score) in enumerate(scores):
            values[index], lefts[index], rights[index] = score.to_triplet()
            voting_rights[index] = 1. / n_scored_entities[username]
        std_dev = qr_standard_deviation(
            lipschitz=self.lipschitz,
            values=values,
            quantile_dev=self.dev_quantile,
            voting_rights=voting_rights,
            left_uncertainties=lefts,
            right_uncertainties=rights,
            default_dev=1.0,
            error=self.error,
        )
        return Score(1./std_dev, 0, 0)
     
    def save_result(self, state: State, directory: Optional[str]=None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving common scales")
            state.user_models.common_scales.save(directory, "common_scales.csv")
        logger.info("Saving state.json")
        return state.save_instructions(directory)
