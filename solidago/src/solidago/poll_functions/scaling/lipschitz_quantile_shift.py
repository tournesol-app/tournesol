from typing import Callable
from numpy.typing import NDArray

import numpy as np
import logging

logger = logging.getLogger(__name__)

from solidago.poll.scoring.user_models import CommonTranslations
from solidago.primitives import qr_quantile
from solidago.poll import *
from solidago.poll_functions.parallelized import ParallelizedPollFunction


class LipschitzQuantileShift(ParallelizedPollFunction):
    block_parallelization: bool = False
    
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
    
    def _variables(self, user_models: UserModels) -> list[str]: # type: ignore
        return [criterion for criterion in user_models.criteria()]
    
    def _nonargs_list(self,  # type: ignore
        variables: list, 
        entities: Entities,
        user_models: UserModels,
    ) -> list[Scores]:
        scores = user_models(
            entities,
            n_sampled_entities_per_user=self.n_sampled_entities_per_user,
        )
        return [scores.filters(criterion=criterion) for criterion in variables]
    
    def _args(self,  # type: ignore
        variable: str, # Not used
        nonargs, # MultiScore
    ) -> tuple[float, float, NDArray, NDArray, NDArray, NDArray, float]:
        scores = nonargs
        assert isinstance(scores, Scores)
        n_scored_entities = { username: len(s) for (username,), s in scores.iter("username") } # type: ignore
        values, voting_rights = np.zeros(len(scores)), np.zeros(len(scores))
        lefts, rights = np.zeros(len(scores)), np.zeros(len(scores))
        for index, score in enumerate(scores):
            values[index], lefts[index], rights[index] = score.to_triplet()
            voting_rights[index] = 1. / n_scored_entities[score["username"]]
        return self.lipschitz, self.quantile, values, voting_rights, lefts, rights, self.error
    
    @property
    def thread_function(self) -> Callable: # type: ignore
        return qr_quantile
    
    def _process_results(self, variables: list, nonargs_list: list, results: list, args_lists: list, user_models: UserModels) -> UserModels: # type: ignore
        translations = CommonTranslations(keynames=["criterion"])
        for criterion, translation in zip(variables, results):
            translations.set(Score(self.target_score - translation), criterion=criterion)
        return user_models.common_scale(translations=translations, note="lipschitz_quantile_shift")

    def save_result(self, poll: Poll, directory: str | None = None) -> tuple[str, dict]:
        if directory is not None:
            logger.info("Saving common scales")
            poll.user_models.save_table(directory, "common_multipliers")
            poll.user_models.save_table(directory, "common_translations")
        return poll.save_instructions(directory)
