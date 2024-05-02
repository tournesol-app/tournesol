from solidago.pipeline.legacy2023.parameters import PipelineParameters

from tournesol.utils.constants import MEHESTAN_MAX_SCALED_SCORE


class MehestanParameters(PipelineParameters):
    max_squashed_score = MEHESTAN_MAX_SCALED_SCORE
