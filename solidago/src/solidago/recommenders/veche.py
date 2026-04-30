from datetime import datetime
from solidago.poll import *
from .recommender import Recommender

from .representatives import Representative
from .aggregator import Aggregator
from .normalization import Normalization
from .sampler import Sampler


class Veche(Recommender):
    def __init__(self, 
        normalization: Normalization | tuple[str, dict] | None = None,
        aggregator: Aggregator | tuple[str, dict] | None = None,
        sampler: Sampler | tuple[str, dict] | None = None,
        follow_kind: str = "follow", 
        default_representative: tuple[str, dict] | None = None,
        n_sampled_councillors: int | None = None,
    ):
        self.follow_kind = follow_kind
        self.default_representative = default_representative or ("Representative", dict())
        self.n_sampled_councillors = n_sampled_councillors
        
        import solidago
        from solidago.recommenders import normalization as n, aggregator as a, sampler as s
        self.normalization = solidago.load(normalization, n, Normalization, n.Norm(q=1))
        self.aggregator = solidago.load(aggregator, a, Aggregator, a.Average())
        self.sampler = solidago.load(sampler, s, Sampler,s.SamplingWithoutReplacement())

    def __call__(self, 
        poll: Poll, 
        limit: int, 
        receiver_name: str | None = None, 
        cursor: str | None = None
    ) -> Entities:
        receiver = poll.users[receiver_name]
        follows = poll.socials.filters(by=receiver_name, kind=self.follow_kind)
        councillors = poll.users.filters(follows.get_column("to"))
        councillors = councillors.assign(volume=follows.get_column("weight"))
        councillors = councillors.sample(self.n_sampled_councillors)
        representative_names = councillors.get_column("representative")\
            .map(lambda x: self.default_representative if x == "default" else x)
        councillors = councillors.assign(representative=representative_names)

        ballots = Scores(keynames=("councillor_name", "entity_name"))
        import solidago
        args = solidago.recommenders.representatives, Representative, self.default_representative
        for c in councillors:
            representative = solidago.load(c["representative"], *args, councillor=c)
            ballot = representative(receiver, datetime.now())
            ballots = ballots | self.normalization(ballot)
        weights = self.aggregator(councillors, poll.entities, ballots)
        return self.sampler(weights, limit)
    