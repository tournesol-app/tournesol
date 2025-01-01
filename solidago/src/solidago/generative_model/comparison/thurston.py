from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import numpy as np

from solidago.state import *
from .base import ComparisonGenerator


class ThurstonComparisonGenerator(ComparisonGenerator):
    def __init__(self, comparison_max: float=float("inf")):
        """ Louis Leon Thurston is a psychologist who modeled comparisons as resulting
        from an evaluation of alternative scores on a common scale,
        and the comparison was then a noisy function of the score difference.
        This class generates comparisons by conforming to the Thurston model. """
        assert comparison_max > 0
        self.comparison_max = comparison_max
    
    def score_matrix(self, users: VectorUsers, entities: VectorEntities):
        return users.vectors @ entities.vectors.T / users.vectors.shape[1]
    
    def sample(self, user: User, left: Entity, right: Entity, left_public: bool, right_public: bool) -> tuple[float, float]:
        """ `lpublic` and `rpublic` are not used.
        Returns comparison max and value. """
        score_diff = (user.vector @ (right.vector - left.vector)) / np.sqrt(user.vector.size)
        comparison = self.sample_comparison(score_diff)
        if "is_trustworthy" in user and not user["is_trustworthy"]:
            comparison = - comparison
        return comparison, self.comparison_max
    
    @abstractmethod
    def sample_comparison(self, score_diff: float) -> float:
        raise NotImplementedError


class DiscreteGBT(ThurstonComparisonGenerator):
    """ The Generalized Bradley-Terry model is a score-to-comparison model
    with numerous desirable properties, which was introduced in the paper
    "Generalized Bradley-Terry Models for Score Estimation from Paired Comparisons"
    by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang and Oscar Villemaud,
    published at AAAI 2024. """
    def __init__(self, comparison_max: float=float("inf")):
        super().__init__(comparison_max)

    @abstractmethod
    def root_law(self, comparison: float) -> float:
        """ This is the function f in the paper.
        Depending on discrete/continuous, it may be the probability mass or density function.
        In our implementation, f does not need to correspond to a normalized probability.
        """
        raise NotImplementedError
        
    def non_normalized_probability(self, score_diff: float, comparison: float) -> float:
        return self.root_law(comparison) * np.exp(score_diff * comparison)
        
    def sample_comparison(self, score_diff: float) -> float:
        pf = self.partition_function(score_diff)
        rand = np.random.random()
        cumulative = 0
        for comparison in self.comparison_generator():
            cumulative += self.probability(score_diff, comparison, pf)
            if rand <= cumulative:
                return comparison
        # Returns 0 in case of numerical error
        return 0
        
    @abstractmethod
    def comparison_generator(self) -> float:
        """ Must be a generator """
        raise NotImplementedError
    
    def partition_function(self, score_diff: float) -> float:
        """ Adds up non all normalized probabilities
        This function must be redefined for root laws with infinite supports
        """
        total = 0
        for comparison in self.comparison_generator():
            total += self.non_normalized_probability(score_diff, comparison)
        return total

    def probability(
        self, 
        score_diff: float, 
        comparison: float, 
        partition_fn: Optional[float] = None
    ) -> float:
        if partition_fn is None:
            partition_fn = self.partition_function(score_diff)
        return self.non_normalized_probability(score_diff, comparison) / partition_fn


class KnaryGBT(DiscreteGBT):
    def __init__(self, n_options: int = 2, comparison_max: float = 1):
        """ n_options is k in the paper """
        super().__init__(comparison_max)
        assert (n_options >= 2)
        self.n_options = n_options

    def root_law(self, comparison: float) -> float:
        return 1

    def comparison_generator(self):
        delta = 2 * self.comparison_max / (self.n_options - 1)
        for k in range(self.n_options):
            yield k * delta - self.comparison_max
 
    def __str__(self):
        return f"K-naryGBT(K={self.n_options}, comparison_max={self.comparison_max})"
        
    def to_json(self):
        return type(self).__name__, dict(
            n_options=self.n_options, comparison_max=self.comparison_max
        )
