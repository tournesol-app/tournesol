from copy import deepcopy
from functools import reduce
from typing import Hashable

from solidago.poll import *
from solidago.functions.poll_function import PollFunction


class SumCriteria(PollFunction):
    default_weights: dict[str, float] = dict(post=1., repost=1., report=1.)

    def __init__(self, weights: dict[str, float] | None = None, aggregated_name: str = "main"):
        self.weights = weights or self.default_weights
        self.aggregated_name = aggregated_name

    def fn(self, user_models: UserModels, global_model: ScoringModel) -> tuple[UserModels, ScoringModel]:
        user_models, global_model = deepcopy(user_models), deepcopy(global_model)

        for (username, entity_name), subscores in user_models().iter("username", "entity_name"):
            kwargs = dict(username=username, entity_name=entity_name, criterion=self.aggregated_name)
            user_models.user_directs.append(self._add(subscores), **kwargs)

        for (entity_name,), subscores in global_model().iter("entity_name"):
            kwargs = dict(entity_name=entity_name, criterion=self.aggregated_name)
            global_model.directs.append(self._add(subscores), **kwargs)

        return user_models, global_model

    def _add(self, subscores: Scores) -> Score:
        def f(score: Score, criterion: Hashable) -> Score:
            return score + subscores.get(criterion=criterion) * self.weights[str(criterion)]
        return reduce(f, subscores.keys("criterion") & self.weights.keys(), Score(0))


class GlobalSumCriteria(PollFunction):
    default_weights: dict[str, float] = dict(post=1., repost=1., report=1.)

    def __init__(self, weights: dict[str, float] | None = None, aggregated_name: str = "main"):
        self.weights = weights or self.default_weights
        self.aggregated_name = aggregated_name

    def fn(self, global_model: ScoringModel) -> ScoringModel:
        global_model = ScoringModel()

        for (entity_name,), subscores in global_model().iter("entity_name"):
            kwargs = dict(entity_name=entity_name, criterion=self.aggregated_name)
            global_model.directs.append(self._add(subscores), **kwargs)

        return global_model

    def _add(self, subscores: Scores) -> Score:
        def f(score: Score, criterion: Hashable) -> Score:
            return score + subscores.get(criterion=criterion) * self.weights[str(criterion)]
        return reduce(f, subscores.keys("criterion") & self.weights.keys(), Score(0))
