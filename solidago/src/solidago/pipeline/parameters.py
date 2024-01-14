from dataclasses import dataclass
from functools import cached_property

from solidago.comparisons_to_scores import ContinuousBradleyTerry


@dataclass
class PipelineParameters:
    # comparisons to scores
    alpha: float = 0.02
    r_max: float = 10.0

    # collaborative scaling and aggregation
    max_squashed_score: float = 100.0
    score_shift_W: float = 1.
    score_shift_quantile: float = 0.15
    score_deviation_quantile: float = 0.9
    W: float = 10.0

    # voting rights
    vote_weight_public_ratings = 1.0
    vote_weight_private_ratings = 0.5

    @cached_property
    def indiv_algo(self):
        return ContinuousBradleyTerry(r_max=self.r_max, alpha=self.alpha)
