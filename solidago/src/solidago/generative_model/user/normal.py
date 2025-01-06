from typing import Optional, Iterable, Union
from numpy.random import random, poisson, zipf, gamma, normal

import numpy as np

from solidago.state import *
from .base import UserGenerator


class NormalUserGenerator(UserGenerator):
    users_cls: type=VectorUsers
    
    def __init__(
        self,
        n_users: int=30,
        p_trustworthy: float=0.8,
        p_pretrusted: float=0.2,
        zipf_vouch: float=2.0,
        zipf_compare: float=1.5,
        poisson_compare: float=30.0,
        n_comparisons_per_entity: float=3.0,
        multiplicator_std_dev: float=0.0,
        engagement_bias_std_dev: float=0.0,
        mean: Optional[Union[float, list[float]]]=None, 
        dimension: Optional[int]=None,
    ):
        """ This models users, with varying vouch, engagement and multiplicative scaling behaviors.
        Users are also given a normally distributed vector representation.
        
        Parameters
        ----------
        n_users: int=30
            Number of users generated
        p_trustworthy: float=0.8
            Probability that a user is trustworthy
        p_pretrusted: float=0.5
            Probability that a trusworthy user is pretrusted
        zipf_vouch: float=2.0
            Assumes that the expected number of vouches of a user follows a Zipf law
            zipf_vouch is the expectation of this Zipf law
        zipf_compare: float=1.5
        poisson_compare: float=30.0
            Assumes that the expected number of comparisons per entity of a user follows 
            a sum of a Zipf law and a Poisson law
            zipf_compare is the expectation of this Zipf law,
            while poisson_compare is the expectation of the Poisson law
        n_comparisons_per_entity: float=3.0
            Expected number of comparisons per entity
        multiplicator_std_dev: float=0.0
            Users may use varying multiplicative scales to compare entities (e.g in Bradley-Terry)
            The scale multiplicator follows a gamma distribution of mean 1,
            and whose standard deviation is multiplicator_std_dev
        engagement_bias_std_dev: float=0.0
            Assumes that, when they select entities to compare, 
            different users may be more or less biased towards selecting their preferred entities
            A positive value means that preferred entities tend to be more evaluated
        mean: mean of the vector representation
            Mean of the vector representations of the entities and of the users
        dimension: int or None (default)
            Dimension of the vector representations
        """
        assert p_trustworthy >= 0 and p_trustworthy <= 1
        assert p_pretrusted >= 0 and p_pretrusted <= 1
        assert zipf_vouch > 1.0 and zipf_compare > 1.0
        assert poisson_compare > 0 and n_comparisons_per_entity > 0
        assert mean is not None or dimension is not None
        super().__init__(n_users)
        if isinstance(mean, Iterable) and dimension is not None:
            assert len(mean) == dimension
            mean = np.array(mean)
        elif mean is None:
            mean = np.zeros(dimension)
        elif isinstance(mean, (int, float)):
            mean = np.zeros(dimension) + mean
        
        self.p_trustworthy = p_trustworthy
        self.p_pretrusted = p_pretrusted
        self.zipf_vouch = zipf_vouch
        self.zipf_compare = zipf_compare
        self.poisson_compare = poisson_compare
        self.n_comparisons_per_entity = n_comparisons_per_entity
        self.multiplicator_std_dev = multiplicator_std_dev
        self.engagement_bias_std_dev = engagement_bias_std_dev
        self.mean = list(mean)
    
    def vector_sample(self):
        return np.random.normal(0, 1, len(self.mean)) + np.array(self.mean)

    def sample(self, username: str):
        user = self.users_cls.series_cls(self.vector_sample(), name=username)
        user["is_trustworthy"] = (random() < self.p_trustworthy)
        user["is_pretrusted"] = (random() < self.p_pretrusted) if user["is_trustworthy"] else False
        user["n_expected_vouches"] = zipf(self.zipf_vouch) - 1
        user["n_comparisons"] = zipf(self.zipf_compare) + poisson(self.poisson_compare)
        user["n_comparisons_per_entity"] = 1 + poisson(self.n_comparisons_per_entity)
        user["multiplicator"] = 1 if self.multiplicator_std_dev == 0 else gamma(
            shape=self.multiplicator_std_dev ** -2,
            scale=self.multiplicator_std_dev ** 2
        )
        user["engagement_bias"] = normal(0, self.engagement_bias_std_dev)
        return user

    @classmethod
    def json_keys(cls):
        return ["n_users", "p_trustworthy", "p_pretrusted", "zipf_vouch", "zipf_compare", 
            "poisson_compare", "n_comparisons_per_entity", "mean", 
            "multiplicator_std_dev", "engagement_bias_std_dev"]
