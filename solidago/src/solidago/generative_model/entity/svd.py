from typing import Iterable, Callable, Union
import numpy as np

from typing import Optional, Callable
from solidago.state import Entities
from .base import EntityGenerator


class SvdEntityGenerator(EntityGenerator):
    def __init__(self, svd_dimension: int=3, svd_distribution: Optional[Callable]=None):
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
        if svd_distribution is None:
            self.svd_distribution = lambda: np.random.normal(0, 1, self.svd_dimension)
        else:
            self.svd_distribution = svd_distribution

    def user_generate(self):
        svd = self.svd_distribution()
        return pd.Series({ f"svd{i}": svd[i] for i in range(self.svd_dimension) })

    def __str__(self):
        return f"SvdEntityModel(svd_dimension={self.svd_dimension})"

    def to_json(self):
        return type(self).__name__, dict(svd_dimension=self.svd_dimension)


class NormalEntityGenerator(SvdEntityGenerator):
    def __init__(self, mean: Union[int, float, Iterable]=0, svd_dimension: Optional[int]=None):
        """ Svd entity generation based on normally distributed features.
        
        Parameters
        ----------
        mean: int, float ou numpy array
            Mean of the distribution
        svd_distribution: callable
            Given svd_dimension, generates a random vector
        """
        assert mean is not None or svd_dimension is not None
        if isinstance(mean, Iterable) and svd_dimension is not None:
            assert len(list(mean)) == svd_dimension
        if isinstance(mean, (int, float)):
            mean = np.zeros(svd_dimension) + mean
        super().__init__(len(mean), lambda: np.random.normal(0, 1, len(mean)) + mean)
        self.mean = mean

    def __str__(self):
        return f"NormalEntityModel(mean={list(self.mean)})"

    def to_json(self):
        return type(self).__name__, dict(mean=list(self.mean))

