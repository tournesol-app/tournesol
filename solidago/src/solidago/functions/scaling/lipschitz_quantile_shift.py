from typing import Callable

import numpy as np
import logging

logger = logging.getLogger(__name__)

from solidago.primitives import qr_quantile
from solidago.poll import *
from solidago.functions.parallelized import ParallelizedPollFunction


class LipschitzQuantileShift(ParallelizedPollFunction):
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
    
    def _variables(self, user_models: UserModels) -> list[str]:
        return [criterion for criterion in user_models.criteria()]
    
    def _args(self, variable: str, nonargs, entities: Entities, user_models: UserModels):
        assert isinstance(variable, str), variable
        assert isinstance(entities, Entities), entities
        assert isinstance(user_models, UserModels), user_models
        scores = user_models(entities, variable, self.n_sampled_entities_per_user) # variable == criterion
        n_scored_entities = { username: len(s) for (username,), s in scores.iter("username") }
        values, voting_rights = np.zeros(len(scores)), np.zeros(len(scores))
        lefts, rights = np.zeros(len(scores)), np.zeros(len(scores))
        for index, ((username, _), score) in enumerate(scores):
            values[index], lefts[index], rights[index] = score.to_triplet()
            voting_rights[index] = 1. / n_scored_entities[username]
        return self.lipschitz, self.quantile, values, voting_rights, lefts, rights, self.error
    
    @property
    def thread_function(self) -> Callable:
        return qr_quantile
    
    def _process_results(self, variables: list, nonargs_list: list, results: list, args_lists: list, user_models: UserModels) -> UserModels:
        scales = MultiScore(["kind", "criterion"])
        for criterion, translation in zip(variables, results):
            scales["multiplier", criterion] = Score(self.target_score - translation, 0, 0)
        return user_models.scale(scales, note="lipschitz_standardardize")

    def save_result(self, poll: Poll, directory: str | None = None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving common scales")
            poll.user_models.save_common_scales(directory)
        return poll.save_instructions(directory)
