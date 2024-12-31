from typing import Iterable, Callable, Union
from numpy.random import normal

import numpy as np

from typing import Optional, Callable
from solidago.state import VectorEntity, VectorEntities
from .base import EntityGenerator


class NormalEntityGenerator(EntityGenerator):
    entities_cls: type=VectorEntities
    
    def __init__(self, 
        n_entities: int=100,
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
        super().__init__(n_entities)
        assert mean is not None or dimension is not None
        if isinstance(mean, Iterable) and dimension is not None:
            assert len(mean) == dimension
            mean = np.array(mean)
        elif isinstance(mean, (int, float)):
            mean = np.zeros(dimension) + mean
        elif mean is None:
            mean = np.zeros(dimension)
        self.mean = mean
    
    def sample(self, entity_name):
        return VectorEntity(self.sample_vector(), name=entity_name)

    def sample_vector(self) -> np.ndarray:
        return np.random.normal(0, 1, len(self.mean)) + self.mean

    def __str__(self):
        return f"NormalEntityGenerator(mean={self.mean})"

    def to_json(self):
        return type(self).__name__, dict(mean=self.mean)
