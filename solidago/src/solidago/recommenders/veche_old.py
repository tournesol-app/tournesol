from datetime import datetime

from solidago.poll import *

from .recommender import Recommender
from .moderation import Moderation
from .volumes import Volumes
from .bias import BallotBiasing
from .normalization import Normalization
from .aggregator import Aggregator
from .sampler import Sampler


class Veche(Recommender):
    def __init__(self, 
        moderations: list[Moderation | tuple[str, dict]] | None = None,
        volumes: Volumes | tuple[str, dict] | None = None,
        biases: list[BallotBiasing | tuple[str, dict]] | None = None,
        normalization: Normalization | tuple[str, dict] | None = None,
        aggregator: Aggregator | tuple[str, dict] | None = None,
        sampler: Sampler | tuple[str, dict] | None = None,
    ):        
        import solidago
        from solidago.recommenders import moderation as m, volumes as v, bias as b
        from solidago.recommenders import normalization as n, aggregator as a, sampler as s
        self.moderations = [solidago.load(mod, m, Moderation) for mod in moderations or list()]
        self.volumes = solidago.load(volumes, v, Volumes, v.Follows())
        self.biases = [solidago.load(bias, b, BallotBiasing) for bias in biases or list()]
        self.normalization = solidago.load(normalization, n, Normalization, n.Norm(q=1))
        self.aggregator = solidago.load(aggregator, a, Aggregator, a.Sum())
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
        for moderation in self.moderations:
            poll = moderation(poll, receiver, time)
        councillors = self.volumes(poll, receiver, time)
        ballots = Scores(keynames=("councillor_name", "entity_name"))
        import solidago, solidago.recommenders.representatives as r
        for c in councillors:
            representative = solidago.load(c["representative"], r, r.Representative)
            ballot = representative(poll, c, receiver, time)
            for bias in self.biases:
                ballot = bias(poll, ballot)
            ballots = ballots | self.normalization(ballot)
        weighted_entities = self.aggregator(poll, councillors, ballots)
        return self.sampler(poll, weighted_entities, ballots, limit)
    