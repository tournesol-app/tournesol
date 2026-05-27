from solidago.poll import *
from solidago.functions import PollFunction
from solidago.primitives.time import Date, DateInput
from .recommender import Recommender
from .sampler import Sampler


class Veche(Recommender):
    def __init__(self, 
        preprocess: PollFunction | tuple[str, dict] | None = None,
        sampler: Sampler | tuple[str, dict] | None = None,        
    ):        
        import solidago, solidago.functions as f, solidago.recommenders.sampler as s
        self.preprocess = solidago.load(preprocess, f, PollFunction, f.Sequential([
            f.filtering.RemoveAuthoredEntities(),
            f.filtering.RemoveRecommendedEntities(),
            f.voting_rights.Follows(),
            f.voting_rights.LikesVolumes(),
            f.voting_rights.Mentions(),
            f.voting_rights.AggregateVolumes(),
            f.trust_propagation.Liquid(),
            f.filtering.PositiveVotingRightOnly(),
            f.preference_learning.PostActions(),
            f.collaborative_filtering.Liquid(),
            f.preference_bias.TimeDecay(),
            f.preference_bias.Discoverability(),
            f.preference_bias.LifetimeBias(),
            f.preference_bias.SemanticBias(),
            f.scaling.MaxNorm(),
            f.aggregation.Sum(),
            f.post_process.SumCriteria(),
        ]))
        self.sampler = solidago.load(sampler, s, Sampler, s.SamplingWithoutReplacement())

    def customize(self,
        receiver_name: str | None = None, 
        date: DateInput | None = None,
    ):
        d = Date.now() if date is None else Date(date)
        self.preprocess.customize(receiver_name, d)        

    def __call__(self, 
        poll: Poll, 
        limit: int, 
        receiver_name: str | None = None, 
        cursor: str | None = None,
        date: DateInput | None = None,
    ) -> Entities:
        self.customize(receiver_name, date)
        poll = self.preprocess(poll)
        return self.sampler(poll, limit)
    