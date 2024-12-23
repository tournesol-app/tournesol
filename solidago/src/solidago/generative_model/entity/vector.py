from typing import Iterable, Callable, Union
from numpy.random import normal

import numpy as np

from typing import Optional, Callable
from solidago.state import VectorEntity, VectorEntities
from .base import EntityGenerator


class NormalEntityGenerator(EntityGenerator):
    def __init__(self, 
        mean: Optional[Union[int, float, list[float]]]=[3, 0, 0], 
        dimension: Optional[int]=None
    ):
        """ Assigns a normally distributed vector to each entity
        
        Parameters
        ----------
        mean: None or number or list[float]
            Mean of the entity vector distribution
        dimension: None or int
            Dimension of the entity vector distribution (for type(mean) in (NoneType, float))
        """
        assert mean is not None or dimension is not None
        if isinstance(mean, Iterable) and dimension is not None:
            assert len(mean) == dimension
            mean = np.array(mean)
        elif isinstance(mean, (int, float)):
            mean = np.zeros(dimension) + mean
        elif mean is None:
            mean = np.zeros(dimension)
        self.mean = mean

    def sample_vector(self) -> np.ndarray:
        return np.random.normal(0, 1, len(self.mean)) + self.mean

    def __call__(self, n_entities: int) -> VectorEntities:
        return VectorEntities([ self.sample(entity_id) for entity_id in range(n_entities) ])
    
    def sample(self, entity_id):
        return VectorEntity(entity_id, self.sample_vector())

    def __str__(self):
        return f"NormalEntityGenerator(mean={self.mean})"

    def to_json(self):
        return type(self).__name__, dict(mean=self.mean)
