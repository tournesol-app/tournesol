import numpy as np

from solidago.poll import *
from solidago.functions.poll_function import PollFunction


class SumCriteria(PollFunction):
    default_weights: dict[str, float] = dict(post=1., repost=1., report=1.)

    def __init__(self, weights: dict[str, float] | None = None, aggregated_name: str = "main"):
        self.weights = weights or self.default_weights
        self.aggregated_name = aggregated_name

    def fn(self, global_model: ScoringModel) -> ScoringModel:
        scores = global_model()
        assert isinstance(scores, Scores)
        for (entity_name,), subscores in scores.iter("entity_name"):
            assert isinstance(subscores, Scores)
            score, criteria = Score(0), subscores.keys("criterion")
            for criterion, weight in self.default_weights.items():
                if criterion in criteria:
                    score = score + subscores.get(None, criterion=criterion) * weight
            global_model.directs.append(score, entity_name=entity_name, criterion=self.aggregated_name)
        return global_model 
