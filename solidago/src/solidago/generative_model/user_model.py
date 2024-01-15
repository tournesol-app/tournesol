from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

class UserModel(ABC):
    @abstractmethod
    def __call__(self, n_users):
        """ Generates n_users users, with different characteristics
        
        Returns:
        - users: DataFrame with columns
            * `user_id`: int
            * `is_pretrusted`: bool
            * And maybe more
        """
        raise NotImplementedError

class SvdUserModel(UserModel):
    def __init__(
        self, 
        svd_dimension: int = 5,
        svd_distribution: callable = lambda dim: np.random.normal(1, 1, dim)
    ):
        """ This model assumes each user's preferences can be represented by a vector in 
        a singular value decomposition. This assumes entities will have such a representation
        as well. To model the fact that users mostly agree, we assume that the center of
        the distribution equals the standard deviation
        
        Inputs:
        - svd_dimension is the dimension of the vector representation
        - svd_distribution inputs the svd_dimension, and generates a random vector
        """
        self.svd_dimension = svd_dimension
        self.svd_distribution = svd_distribution
    
    def generate_svd(self):
        return self.svd_distribution(self.svd_dimension)
        
    def __call__(self, n_users: int):
        dct = dict(
            is_pretrusted = [np.random.randint(2) == 1 for _ in range(n_users)],
            entity_comparison_bias = [np.random.normal() for _ in range(n_users)]
        )
        svd_representations = [self.generate_svd() for _ in range(n_users)]
        for i in range(self.svd_dimension):
            dct[f"svd{i}"] = [svd_representations[u][i] for u in range(n_users)]
        
        return pd.DataFrame(dct)
