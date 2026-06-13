from solidago.poll import *
from solidago.functions import PollFunction
from solidago.primitives.datastructure.named_objects import After, Before
from solidago.primitives.time import Date, DateInput
from .recommender import Recommender
from .sampler import Sampler


class Veche(Recommender):
    def __init__(self, 
        preprocess: PollFunction | tuple[str, dict] | None = None,
        sampler: Sampler | tuple[str, dict] | None = None,
        criteria: tuple[str, ...] = ("post", "repost", "report"),
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
        self.criteria = criteria

    def customize(self,
        receiver_name: str | None = None, 
        date: Date | DateInput | None = None,
    ):
        date = Date(date) if isinstance(date, DateInput) else date
        d = Date.now() if date is None else date
        self.preprocess.customize(receiver_name, d)        

    def __call__(self, 
        poll: Poll, 
        limit: int, 
        receiver_name: str | None = None, 
        cursor: str | None = None,
        date: Date | DateInput | None = None,
    ) -> Entities:
        self.customize(receiver_name, date)
        with self.timeit(f"{type(self).__name__} preprocessing", unit="ms"):
            poll = self.preprocess(poll)
        with self.timeit(f"{type(self).__name__} sampling", unit="ms"):
            entities = self.sampler(poll, limit)
        recommenders, recommender_weights = list(), list()
        derecommenders, derecommender_weights = list(), list()
        scores = poll.user_models(entities, self.criteria)
        for entity in entities:
            subscores = scores.filters(entity_name=entity.name, criterion=self.criteria)
            positive = subscores.filters(value=After(0))
            recommenders.append(tuple(positive("username")))
            recommender_weights.append(tuple(positive.value))
            negative = subscores.filters(value=Before(0))
            derecommenders.append(tuple(negative("username")))
            derecommender_weights.append(tuple(negative.value))
        return entities.assign(
            recommenders=recommenders, recommender_weights=recommender_weights,
            derecommenders=derecommenders, derecommender_weights=derecommender_weights
        )