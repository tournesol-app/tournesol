from typing import Optional
from numpy.random import random, poison, zipf, gamma, normal

from solidago.state import Users
from .base import UserGenerator


class NormalUserGenerator(UserGenerator):
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
        svd_mean: mean of the svd representation
            Mean of the svd representations of the entities and of the users
        svd_dimension: int or None (default)
            Dimension of the svd representations
        """
        assert p_trustworthy >= 0 and p_trustworthy <= 1
        assert p_pretrusted >= 0 and p_pretrusted <= 1
        assert zipf_vouch > 1.0 and zipf_compare > 1.0
        assert poisson_compare > 0 and n_comparisons_per_entity > 0
        assert svd_mean is not None or svd_dimension is not None
        if svd_mean is None and svd_dimension is None:
            assert len(mean) == svd_dimension
        if isinstance(svd_mean, (int, float)):
            svd_mean = np.zeros(svd_dimension) + svd_mean
        
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

    def user_generate(self):
        u = pd.Series()
        u["is_trustworthy"] = (random() < self.p_trustworthy)
        u["is_pretrusted"] = (random() < self.p_pretrusted) if u["is_trustworthy"] else False
        u["n_expected_vouches"] = zipf(self.zipf_vouch) - 1
        u["n_comparisons"] = zipf(self.zipf_compare) + poisson(self.poisson_compare)
        u["n_comparisons_per_entity"] = 1 + poisson(self.n_comparisons_per_entity)
        u["multiplicator"] = 1 if self.multiplicator_std_dev == 0 else gamma(
            shape=self.multiplicator_std_dev ** -2,
            scale=self.multiplicator_std_dev ** 2
        )
        u["engagement_bias"] = normal(0, self.engagement_bias_std_dev)
        for i in range(len(self.svd_mean)):
            u[f"svd{i}"] = normal(0, 1) + self.svd_mean[i]
        return u
        
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
