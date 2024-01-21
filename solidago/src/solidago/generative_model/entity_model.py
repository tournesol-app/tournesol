from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

class EntityModel(ABC):
    @abstractmethod
    def __call__(self, n_entities: int) -> pd.DataFrame:
        """ Generates n_entities entities, with different characteristics
        
        Parameters
        ----------
        n_entities: int
            Number of entities to generate.
        
        Returns
        -------
        entities: DataFrame with columns
            * `entity_id`: int, index
            * And maybe more
        """
        raise NotImplementedError

    def __str__(self):
        return type(self).__name__

class SvdEntityModel(EntityModel):
    def __init__(
        self, 
        svd_dimension: int = 5,
        svd_distribution: callable = lambda dim: np.random.normal(1, 1, dim)
    ):
        """ This model assumes each entity can be represented by a vector in a singular 
        value decomposition. This assumes user preferences will have such a representation
        as well. To model the fact that users mostly agree, we assume that the center of
        the distribution equals the standard deviation.
        
        Parameters
        ----------
        svd_dimension: int 
            Dimension of the vector representation
        svd_distribution: callable
            Given svd_dimension, generates a random vector
        """
        self.svd_dimension = svd_dimension
        self.svd_distribution = svd_distribution        

    def __call__(self, n_entities: int):
        """ Generates n_users users, with different characteristics
        
        Parameters
        ----------
        n_entities: int
            Number of entities to generate.
        
        Returns
        -------
        entities: DataFrame with columns
            * `entity_id`: int
            * for each i in range(self.svd_dimension), `svd{i}`: float
        """
        dct = dict()
        svd = [self.svd_distribution(self.svd_dimension) for _ in range(n_entities)]
        df = pd.DataFrame({
            f"svd{i}": [svd[e][i] for e in range(n_entities)]
            for i in range(self.svd_dimension)
        })
        df.index.name = "entity_id"
        return df

    def __str__(self):
        return f"SvdEntityModel(svd_dimension={self.svd_dimension})"
