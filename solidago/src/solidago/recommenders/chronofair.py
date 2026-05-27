from solidago.primitives.decay import QuadraticDecay
from .veche import Veche


class ChronoFair(Veche):
    def __init__(self):
        import solidago.functions as f, solidago.recommenders.sampler as s
        super().__init__(f.Sequential([
            f.filtering.RemoveAuthoredEntities(),
            f.filtering.RemoveRecommendedEntities(),
            f.voting_rights.Follows(),
            f.voting_rights.Mentions(),
            f.voting_rights.AggregateVolumes(),
            f.filtering.PositiveVotingRightOnly(),
            f.preference_learning.PostActions(max_workers=1),
            f.preference_bias.TimeDecay(QuadraticDecay(), max_workers=1),
            f.scaling.MaxNorm(default_q=1.),
            f.aggregation.Sum(max_workers=1),
            f.post_process.SumCriteria(),
        ]), s.SamplingWithoutReplacement())

