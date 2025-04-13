from typing import Iterable, Callable, Optional, Union
from numpy.random import normal

import numpy as np

from solidago.state import *
from .base import EntityGen


class NormalEntity(EntityGen):
    def __init__(self, 
        n_entities: int=100,
        mean: Optional[Union[int, float, list[float]]]=None, 
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
        if mean is None and dimension is None:
            mean = [3, 0, 0]
        if isinstance(mean, Iterable) and dimension is not None:
            assert len(mean) == dimension
            mean = np.array(mean)
        elif isinstance(mean, (int, float)):
            mean = np.zeros(dimension) + mean
        elif mean is None:
            mean = np.zeros(dimension)
        self.mean = mean
    
    def sample(self, entity_name: str) -> Entity:
        return Entity(entity_name, self.sample_vector())

    def sample_vector(self) -> np.ndarray:
        return np.random.normal(0, 1, len(self.mean)) + self.mean
