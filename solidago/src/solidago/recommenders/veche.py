from datetime import datetime

from solidago.poll import *
from solidago.functions import PollFunction
from .recommender import Recommender
from .sampler import Sampler


class Veche(Recommender):
    def __init__(self, 
        preprocess: PollFunction | tuple[str, dict] | None = None,
        sampler: Sampler | tuple[str, dict] | None = None,
    ):        
        import solidago, solidago.functions as f, solidago.recommenders.sampler as s
        self.preprocess = solidago.load(preprocess, f, PollFunction, f.Sequential([
            f.filtering.RemoveRecommendedEntities(),
            f.voting_rights.Follows(),
            f.voting_rights.LikesVolumes(),
            f.voting_rights.Mentions(),
            f.voting_rights.AggregateVolumes(),
            f.trust_propagation.Liquid(),
            f.filtering.IncludedUsersOnly(),
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

    def __call__(self, 
        poll: Poll, 
        limit: int, 
        receiver_name: str | None = None, 
        cursor: str | None = None,
        time: int | None = None,
    ) -> Entities:
        receiver = poll.users[receiver_name]
        time = datetime.now().second if time is None else time
        poll = self.preprocess.customize(receiver, time)(poll)
        return self.sampler(poll, limit)
    