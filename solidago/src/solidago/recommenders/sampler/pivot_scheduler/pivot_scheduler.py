from abc import abstractmethod
import numpy as np
from solidago.poll import *


class PivotScheduler:
    @abstractmethod
    def __call__(self, poll: Poll, entities: Entities) -> tuple[Entity, Entity]:
        raise NotImplemented
    

class Uniform:
    def __call__(self, poll: Poll, entities: Entities) -> tuple[Entity, Entity]:
        i, j = np.random.choice(entities.names(), 2, False)
        return entities[i], entities[j]


class BallotCorrelation:
    def __init__(self, bias: float = 1., criterion: str = "main", epsilon: float=1e-6):
        assert bias >= 0.
        self.bias = bias
        self.criterion = criterion
        self.epsilon = epsilon

    def __call__(self, poll: Poll, entities: Entities) -> tuple[Entity, Entity]:
        if self.bias == 0.:
            return Uniform()(poll, entities)
        values = poll.user_models.to_matrices(poll.users, entities, self.criterion)[0]
        values = np.nan_to_num(values, nan=0.)
        with np.errstate(divide="ignore"):
            correlations = np.nan_to_num(np.corrcoef(values.T), nan=0.)
        lefts, rights = np.where(correlations > 1 - self.epsilon)
        if len(lefts) > 0:
            index = np.random.choice(len(lefts))
            return entities[lefts[index]], entities[rights[index]]
        weights = np.power((1 + correlations) / (1 - correlations), self.bias)
        np.fill_diagonal(weights, 0)
        x = np.random.choice(weights.size, p=weights.reshape(-1))
        left, right = x // len(weights), x % len(weights)
        return entities[left], entities[right]