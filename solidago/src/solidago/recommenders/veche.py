from datetime import datetime

from solidago.poll import *
from solidago.poll_functions import PollFunction
from .recommender import Recommender
from .sampler import Sampler


class Veche(Recommender):
    def __init__(self, 
        preprocess: PollFunction | tuple[str, dict] | None = None,
        sampler: Sampler | tuple[str, dict] | None = None,
    ):        
        import solidago, solidago.poll_functions as pf, solidago.recommenders.sampler as s
        self.preprocess = solidago.load(preprocess, pf, PollFunction, pf.Sequential([
            pf.filtering.RemoveRecommendedEntities(),
            pf.voting_rights.Follows(),
            pf.voting_rights.LikesVolumes(),
            pf.voting_rights.Mentions(),
            pf.voting_rights.AggregateVolumes(),
            pf.trust_propagation.Liquid(),
            pf.filtering.IncludedUsersOnly(),
            pf.preference_learning.PostActions(),
            # Add biases,
            pf.scaling.MaxNorm(),
            pf.aggregation.Sum(),
            pf.post_process.SumCriteria(),
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
    