from numpy.typing import NDArray

import numpy as np

from solidago.poll import *
from .bias import WeightPreservingBias


class Discoverability(WeightPreservingBias):
    def __init__(self, popularity_indicator: str = "n_views", min: int = 1000, bias: float = 1.):
        assert min >= 1
        self.popularity_indicator = popularity_indicator
        self.min = min
        self.bias = bias

    def _multipliers(self,  # type: ignore
        scores: Scores, 
        entities: Entities
    ) -> tuple[NDArray, NDArray | float, NDArray | float]:
        entities = entities.filters(scores("entity_names"))
        popularities = entities(self.popularity_indicator)
        multipliers = np.power(np.log(self.min) / np.log(self.min + popularities), self.bias)
        return multipliers, 0., 0.