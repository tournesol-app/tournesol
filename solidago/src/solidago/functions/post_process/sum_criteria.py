from copy import deepcopy
from functools import reduce
from typing import Hashable

import numpy as np
from numpy.typing import NDArray

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
        scores = global_model()
        criteria = scores("criterion")
        criterion_weights = np.array([self.weights.get(str(criterion), np.nan) for criterion in criteria])
        in_weights = ~np.isnan(criterion_weights)

        entity_names = scores("entity_name")[in_weights]
        weights = criterion_weights[in_weights]
        values = scores.value[in_weights] * weights
        left_uncs = scores.left_unc[in_weights]
        right_uncs = scores.right_unc[in_weights]

        # A negative weight flips the asymmetric uncertainties, as in Score.__mul__.
        weight_is_positive = weights >= 0
        lefts = np.where(weight_is_positive, left_uncs * weights, -right_uncs * weights)
        rights = np.where(weight_is_positive, right_uncs * weights, -left_uncs * weights)

        unique_entities, entity_index = np.unique(entity_names, return_inverse=True)
        def sum_per_entity(per_score_values: NDArray) -> NDArray:
            totals = np.zeros(len(unique_entities))
            np.add.at(totals, entity_index, per_score_values)
            return totals

        rows = list(zip(
            unique_entities,
            [self.aggregated_name] * len(unique_entities),
            sum_per_entity(values),
            sum_per_entity(lefts),
            sum_per_entity(rights),
        ))
        return ScoringModel(directs=DirectScores(rows, columns=["entity_name", "criterion", "value", "left_unc", "right_unc"]))
