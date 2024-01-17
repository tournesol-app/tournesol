from abc import ABC, abstractmethod

import pandas as pd
import numpy as np

class UserModel(ABC):
    @abstractmethod
    def __call__(self, n_users):
        """ Generates n_users users, with different characteristics
        
        Parameters
        ----------
        n_users: int
            Number of users to generate.
        
        Returns
        -------
        users: DataFrame with columns
            * `user_id`: int
            * `is_pretrusted`: bool
            * `is_trustworthy`: bool
            * And maybe more
        """
        raise NotImplementedError
        
    def __str__(self):
        return type(self).__name__

class SvdUserModel(UserModel):
    def __init__(
        self,
        p_trustworthy: float = 0.8,
        p_pretrusted: float = 0.2,
        zipf_vouch: float = 2.0,
        zipf_compare: float = 1.5,
        poisson_compare: float = 30.0,
        n_comparisons_per_entity: float = 3.0,
        svd_dimension: int = 5,
        svd_distribution: callable = lambda dim: np.random.normal(1, 1, dim)
    ):
        """ This model assumes each user's preferences can be represented by a vector in 
        a singular value decomposition. This assumes entities will have such a representation
        as well. To model the fact that users mostly agree, we assume that the center of
        the distribution equals the standard deviation.
        
        Parameters
        ----------
        svd_dimension: int
            Dimension of the vector representation
        svd_distribution: callable
            Given svd_dimension as input, generates a random vector
        """
        assert p_trustworthy >= 0 and p_trustworthy <= 1
        assert p_pretrusted >= 0 and p_pretrusted <= 1
        assert zipf_vouch > 1.0 and zipf_compare > 1.0
        assert poisson_compare > 0 and n_comparisons_per_entity > 0
        assert len(svd_distribution(svd_dimension)) == svd_dimension
        
        self.p_trustworthy = p_trustworthy
        self.p_pretrusted = p_pretrusted
        self.zipf_vouch = zipf_vouch
        self.zipf_compare = zipf_compare
        self.poisson_compare = poisson_compare
        self.n_comparisons_per_entity = n_comparisons_per_entity
        self.svd_dimension = svd_dimension
        self.svd_distribution = svd_distribution
    
    def __call__(self, n_users: int):
        """ Generates n_users users, with different characteristics
                
        Parameters
        ----------
        n_users: int
            Number of users to generate.
        
        Returns
        -------
        users: DataFrame with columns
            * `user_id`: int
            * `is_trustworthy`: bool
            * `is_pretrusted`: bool
            * `n_expected_vouches`: int
            * `n_comparisons`: int
            * `n_comparisons_per_entity`: int
            * for all i in range(self.svd_dimension), `svd{i}`: float
            * And maybe more
        """
        dct = dict(
            is_trustworthy = (np.random.random(n_users) < self.p_trustworthy),
            n_expected_vouches = (np.random.zipf(self.zipf_vouch, n_users) - 1),
        )
        dct["n_comparisons"] = np.random.zipf(self.zipf_compare, n_users) 
        dct["n_comparisons"] += np.random.poisson(self.poisson_compare, n_users)
        dct["n_comparisons_per_entity"] = 1 + np.random.poisson(
            self.n_comparisons_per_entity, 
            n_users
        )
        
        dct["is_pretrusted"] = (np.random.random(n_users) < self.p_pretrusted)
        dct["is_pretrusted"] *= dct["is_trustworthy"]
        
        svd = [self.svd_distribution(self.svd_dimension) for _ in range(n_users)]
        for i in range(self.svd_dimension):
            dct[f"svd{i}"] = [svd[u][i] for u in range(n_users)]
        
        df = pd.DataFrame(dct)
        df.index.name = "user_id"
        return df
        
    def __str__(self):
        printed_properties = ["p_trustworthy", "p_pretrusted", "zipf_vouch",
            "zipf_compare", "poisson_compare", "n_comparisons_per_entity","svd_dimension"]
        properties = ", ".join([f"{p}={getattr(self,p)}" for p in printed_properties])
        return f"SvdUserModel({properties})"
