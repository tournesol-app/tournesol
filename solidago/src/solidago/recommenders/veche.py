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
        n_sampled_voters: int | None = None,
    ):
        self.follow_kind = follow_kind
        self.default_representative = default_representative or ("ChronoRepresentative", dict())
        self.n_sampled_voters = n_sampled_voters
        
        import solidago
        from solidago.recommenders import normalization as n, aggregator as a, sampler as s
        self.normalization = solidago.load(normalization, n, Normalization, n.Norm(q=1))
        self.aggregator = solidago.load(aggregator, a, Aggregator, a.Average())
        self.sampler = solidago.load(sampler, s, Sampler,s.SamplingWithoutReplacement())

    def __call__(self, 
        poll: Poll, 
        username: str, 
        limit: int, 
        cursor: str | None = None
    ) -> Entities:
        user = poll.users[username]
        follows = poll.socials.filters(by=username, kind=self.follow_kind)
        voter_names = follows.get_column("to")
        voters = poll.users.filters(voter_names)
        voters = voters.assign(volume=follows.get_column("weight"))
        voters = voters.sample(self.n_sampled_voters)
        representative_names = voters.get_column("representative")\
            .map(lambda x: self.default_representative if x == "default" else x)
        voters = voters.assign(representative=representative_names)

        ballots = Scores(keynames=("username", "entity_name"))
        for voter in voters:
            import solidago, solidago.recommenders.representatives as m
            r = solidago.load(voter["representative"], m, Representative, 
                self.default_representative, user=voter)
            ballots = ballots | self.normalization(r(user))
        weights = self.aggregator(voters, poll.entities, ballots)
        return self.sampler(weights, limit)
    