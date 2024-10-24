from abc import ABC, abstractmethod
from typing import Optional

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

    def to_json(self):
        return (type(self).__name__, )

class NormalUserModel(UserModel):
    def __init__(
        self,
        p_trustworthy: float=0.8,
        p_pretrusted: float=0.2,
        zipf_vouch: float=2.0,
        zipf_compare: float=1.5,
        poisson_compare: float=30.0,
        n_comparisons_per_entity: float=3.0,
        multiplicator_std_dev: float=0.0,
        engagement_bias_std_dev: float=0.0,
        svd_mean: list[float]=[3, 0, 0], 
        svd_dimension: Optional[int]=None,
    ):
        """ This model assumes each user's preferences can be represented by a vector in 
        a singular value decomposition. This assumes entities will have such a representation
        as well. To model the fact that users mostly agree, we assume that the center of
        the distribution equals the standard deviation.
        
        Parameters
        ----------
        p_trustworthy: float=0.8,
        p_pretrusted: float=0.5,
        zipf_vouch: float=2.0,
        zipf_compare: float=1.5,
        poisson_compare: float=30.0,
        n_comparisons_per_entity: float=3.0,
        multiplicator_std_dev: float=0.0,
        engagement_bias_std_dev: float=0.0,
        svd_mean: mean of the svd representation,
        svd_dimension: int or None (default),
        """
        assert p_trustworthy >= 0 and p_trustworthy <= 1
        assert p_pretrusted >= 0 and p_pretrusted <= 1
        assert zipf_vouch > 1.0 and zipf_compare > 1.0
        assert poisson_compare > 0 and n_comparisons_per_entity > 0
        assert svd_mean is not None or svd_dimension is not None
        if svd_mean is None and svd_dimension is None:
            assert len(mean) == svd_dimension
        
        self.p_trustworthy = p_trustworthy
        self.p_pretrusted = p_pretrusted
        self.zipf_vouch = zipf_vouch
        self.zipf_compare = zipf_compare
        self.poisson_compare = poisson_compare
        self.n_comparisons_per_entity = n_comparisons_per_entity
        self.multiplicator_std_dev = multiplicator_std_dev
        self.engagement_bias_std_dev = engagement_bias_std_dev
        self.svd_mean = np.zeros(svd_dimension) if svd_mean is None else np.array(svd_mean)
    
    def svd_sample(self):
        return np.random.normal(0, 1, len(self.svd_mean)) + self.svd_mean
    
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
        
        if self.multiplicator_std_dev == 0:
            dct["multiplicator"] = 1 + np.zeros(n_users)
        else:
            dct["multiplicator"] = np.random.gamma(
                shape=self.multiplicator_std_dev ** -2,
                scale=self.multiplicator_std_dev ** 2,
                size=n_users
            )
        dct["engagement_bias"] = np.random.normal(0, self.engagement_bias_std_dev, n_users)
        
        svd = [self.svd_sample() for _ in range(n_users)]
        for i in range(len(self.svd_mean)):
            dct[f"svd{i}"] = [svd[u][i] for u in range(n_users)]
        
        df = pd.DataFrame(dct)
        df.index.name = "user_id"
        return df
        
    def __str__(self):
        printed_properties = ["p_trustworthy", "p_pretrusted", "zipf_vouch", "zipf_compare", 
            "poisson_compare", "n_comparisons_per_entity", "svd_mean", 
            "multiplicator_std_dev", "engagement_bias_std_dev"]
        properties = ", ".join([f"{p}={getattr(self,p)}" for p in printed_properties])
        return f"SvdUserModel({properties})"

    def to_json(self):
        return type(self).__name__, dict(
            p_trustworthy=self.p_trustworthy,
            p_pretrusted=self.p_pretrusted,
            zipf_vouch=self.zipf_vouch,
            zipf_compare=self.zipf_compare,
            poisson_compare=self.poisson_compare,
            n_comparisons_per_entity=self.n_comparisons_per_entity,
            svd_mean=list(self.svd_mean),
        )
