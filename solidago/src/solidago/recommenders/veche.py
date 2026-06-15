import numpy as np

from solidago.poll import *
from solidago.functions import PollFunction
from solidago.primitives.time import Date, DateInput
from .recommender import Recommender
from .sampler import Sampler


class Veche(Recommender):
    def __init__(self, 
        preprocess: PollFunction | tuple[str, dict] | None = None,
        sampler: Sampler | tuple[str, dict] | None = None,
        criteria: list[str] = ["post", "repost", "report"],
        context: str | None = None,
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
        self.context = type(self).__name__ if context is None else context

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
        with self.timeit(f"{type(self).__name__} recovering recommenders", unit="ms"):
            return self._add_recommenders(entities, poll.user_models)
    
    def _add_recommenders(self, entities: Entities, user_models: UserModels) -> Entities:
        recommenders, recommender_weights = list(), list()
        derecommenders, derecommender_weights = list(), list()
        main_recommenders = list()
        scores = user_models(entities, self.criteria)
        scores = scores.add_columns(positive=scores.value >= 0)
        for entity in entities:
            subscores = scores.filters(entity_name=entity.name, criterion=self.criteria)
            positives = subscores.filters(positive=True)
            recommenders.append(tuple(positives("username")))
            recommender_weights.append(tuple(positives.value))
            probs = positives.value / positives.value.sum()
            main_recommender = np.random.choice(positives("entity_name"), 1, False, probs)[0]
            main_recommenders.append(main_recommender)
            negative = subscores.filters(positive=False)
            derecommenders.append(tuple(negative("username")))
            derecommender_weights.append(tuple(negative.value))
        return entities.assign(
            recommenders=recommenders, recommender_weights=recommender_weights,
            derecommenders=derecommenders, derecommender_weights=derecommender_weights,
            main_recommender=main_recommenders,
        )

    def add_to_history(self, 
        poll: Poll, 
        recommended_entities: Entities,
        receiver_name: str | None = None, 
        cursor: str | None = None,
        date: Date | DateInput | None = None,
    ) -> Poll:
        p = poll.copy()
        date = Date(date) if isinstance(date, DateInput) else date
        d = Date.now() if date is None else date
        recommendations = PastRecommendations(columns=[], keynames=[])\
            .add_columns(entity_name=recommended_entities.names())\
            .add_columns(username=receiver_name, context=self.context, timestamp=d.timestamp())
        recommendations.keynames = ["username", "entity_name"]
        p.past_recommendations = poll.past_recommendations | recommendations
        return p