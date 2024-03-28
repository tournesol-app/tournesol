from solidago.pipeline.legacy2023.parameters import PipelineParameters

from tournesol.utils.constants import COMPARISON_MAX, MEHESTAN_MAX_SCALED_SCORE


class MehestanParameters(PipelineParameters):
    r_max = COMPARISON_MAX
    max_squashed_score = MEHESTAN_MAX_SCALED_SCORE
