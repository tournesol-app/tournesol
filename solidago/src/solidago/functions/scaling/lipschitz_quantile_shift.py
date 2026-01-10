from typing import Optional

import numpy as np
import logging

from solidago.primitives.threading import threading
logger = logging.getLogger(__name__)

from solidago.primitives import qr_quantile
from solidago.poll import *
from solidago.functions.base import PollFunction


class LipschitzQuantileShift(PollFunction):
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
        args_lists = self._args_lists(entities, user_models)
        translations = threading(self.max_workers, qr_quantile, *args_lists)
        scales = MultiScore(["kind", "criterion"])
        for criterion, translation in zip(user_models.criteria(), translations):
            scales["multiplier", criterion] = Score(self.target_score - translation, 0, 0)
        return user_models.scale(scales, note="lipschitz_standardardize")
    
    def _args_lists(self, entities: Entities, user_models: UserModels):
        criteria = user_models.criteria()
        args = [self._args(entities, user_models, c) for c in criteria]
        values, lefts, rights, voting_rights = list(zip(*args))
        lipschitz = [self.lipschitz] * len(criteria)
        quantile = [self.quantile] * len(criteria)
        error = [self.error] * len(criteria)
        return lipschitz, quantile, values, voting_rights, lefts, rights, error
    def _args(self, entities: Entities, user_models: UserModels, criterion: str):
        scores = user_models(entities, criterion, self.n_sampled_entities_per_user)
        n_scored_entities = { username: len(s) for (username,), s in scores.iter("username") }
        values, voting_rights = np.zeros(len(scores)), np.zeros(len(scores))
        lefts, rights = np.zeros(len(scores)), np.zeros(len(scores))
        for index, ((username, _), score) in enumerate(scores):
            values[index], lefts[index], rights[index] = score.to_triplet()
            voting_rights[index] = 1. / n_scored_entities[username]
        return values, lefts, rights, voting_rights
        
    def save_result(self, poll: Poll, directory: Optional[str]=None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving common scales")
            poll.user_models.save_common_scales(directory)
        return poll.save_instructions(directory)
