from typing import Callable
from numpy.typing import NDArray

import numpy as np
import logging

logger = logging.getLogger(__name__)

from solidago.poll.scoring.user_models import CommonMultipliers
from solidago.primitives import qr_standard_deviation
from solidago.poll import *
from solidago.functions.parallelized import ParallelizedPollFunction


class LipschitzStandardize(ParallelizedPollFunction):
    block_parallelization: bool = False
    
    def __init__(self, 
        dev_quantile: float=0.9, 
        lipschitz: float=0.1, 
        error: float=1e-5, 
        n_sampled_entities_per_user: int=100,
        default_dev: float=1.0,
        *args, **kwargs
    ):
        """ The scores are shifted so that their quantile zero_quantile equals zero
        
        Parameters
        ----------
        dev_quantile: float
        """
        super().__init__(*args, **kwargs)
        self.dev_quantile = dev_quantile
        self.lipschitz = lipschitz
        self.error = error
        self.n_sampled_entities_per_user = n_sampled_entities_per_user
        self.default_dev = default_dev
    
    def _variables(self, user_models: UserModels) -> list[str]:
        return [criterion for criterion in user_models.criteria()]
    
    def _nonargs_list(self, 
        variables: list, 
        entities: Entities,
        user_models: UserModels,
    ) -> list[MultiScore]:
        scores = user_models(
            entities,
            n_sampled_entities_per_user=self.n_sampled_entities_per_user,
            keynames=["criterion", "username", "entity_name"],
        )
        return [scores[criterion] for criterion in variables]
    
    def _args(self, 
        variable: str, # Not used
        nonargs, # MultiScore
    ) -> tuple[float, float, NDArray, NDArray, NDArray, NDArray, float]:
        """ variable is criterion """
        scores = nonargs
        n_scored_entities = { username: len(s) for (username,), s in scores.iter("username") }
        values, voting_rights = np.zeros(len(scores)), np.zeros(len(scores))
        lefts, rights = np.zeros(len(scores)), np.zeros(len(scores))
        for index, ((username, _), score) in enumerate(scores):
            values[index], lefts[index], rights[index] = score.to_triplet()
            voting_rights[index] = 1. / n_scored_entities[username]
        return self.lipschitz, values, self.dev_quantile, voting_rights, lefts, rights, self.default_dev, self.error

    @property
    def thread_function(self) -> Callable:
        return qr_standard_deviation
    
    def _process_results(self, variables: list, nonargs_list: list, results: list, args_lists: list, user_models: UserModels) -> UserModels:
        multipliers = CommonMultipliers(["criterion"])
        for criterion, std_dev in zip(variables, results):
            multipliers[criterion] = Score(1./std_dev, 0, 0)
        return user_models.common_scale(multipliers=multipliers, note="lipschitz_standardardize")
    
    def save_result(self, poll: Poll, directory: str | None = None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving common scales")
            poll.user_models.save_table(directory, "common_multipliers")
            poll.user_models.save_table(directory, "common_translations")
        return poll.save_instructions(directory)
