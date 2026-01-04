from abc import abstractmethod
from typing import Union

import numpy as np

from solidago.poll import User, Entities
from solidago.primitives.random import Distribution


class SelectEntities:
    @abstractmethod
    def __call__(self, user: User, entities: Entities) -> Entities:
        """ Selects a subset of entities that the user will evaluate """
        raise NotImplemented
    
    @classmethod
    def load(cls, value: Union["SelectEntities", list, tuple]) -> "SelectEntities":
        if isinstance(value, SelectEntities):
            return value
        assert len(value) == 2
        classname, kwargs = value
        from solidago.generators.engagements import select_entities
        assert hasattr(select_entities, classname), classname
        return getattr(select_entities, classname)(**kwargs)
    
    def __repr__(self):
        t = ".".join(str(type(self)).split(".")[2:])[:-2]
        kwargs = ", ".join([f"{k}={v}" for k, v in self.__dict__.items()])
        return f"{t}({kwargs})"

class Uniform(SelectEntities):
    """ Requires user.n_evaluated_entities """
    def __call__(self, user: User, entities: Entities) -> Entities:
        assert hasattr(user, "n_evaluated_entities"), user
        n_evaluated_entities = user.n_evaluated_entities
        assert isinstance(n_evaluated_entities, (int, np.integer)), n_evaluated_entities
        assert n_evaluated_entities >= 0, n_evaluated_entities
        if n_evaluated_entities > len(entities):
            return entities
        choice = np.random.choice(len(entities), n_evaluated_entities, False)
        return entities[[entities.index2name(i) for i in choice]]

class BiasedByScore(SelectEntities):
    """ Requires user.n_evaluated_entities and user.engagement_bias """
    def __init__(self, noise: Distribution | list | tuple):
        self.noise = Distribution.load(noise)

    def __call__(self, user: User, entities: Entities) -> Entities:
        assert hasattr(user, "n_evaluated_entities"), user
        n_evaluated_entities = user.n_evaluated_entities
        assert isinstance(n_evaluated_entities, (int, np.integer)), n_evaluated_entities

        # To implement engagement bias, we construct a noisy score-based sort of the entities
        scores = entities.vectors @ user.vector
        assert scores.shape == (len(entities),), scores
        noisy_scores = - user.engagement_bias * scores + self.noise.sample(len(scores))
        assert noisy_scores.shape == (len(entities),), noisy_scores
        argsort = np.argsort(noisy_scores)
        
        n_eval_entities = min(len(entities), n_evaluated_entities)
        assert argsort.size == len(entities), argsort
        assert all(isinstance(argsort[i], (int, np.int64)) for i in range(len(entities))), argsort
        return entities[[entities.index2name(argsort[i]) for i in range(n_eval_entities)]]        

