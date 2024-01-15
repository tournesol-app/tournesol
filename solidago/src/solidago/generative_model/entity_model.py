from abc import ABC, abstractmethod

import pandas as pd

class EntityModel(ABC):
    @abstractmethod
    def __call__(self, n_entities):
        """ Generates n_entities entities, with different characteristics
        
        Returns:
        - entities: DataFrame with columns
            * `entity_id`: int
            * And maybe more
        """
        raise NotImplementedError
