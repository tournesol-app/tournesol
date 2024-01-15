from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import numpy as np

class ComparisonModel(ABC):
    @abstractmethod
    def __call__(self, true_scores: pd.DataFrame, comparisons: pd.DataFrame) -> pd.DataFrame:
        """ Assigns a score to each entity, by each user
        Inputs:
        - true_scores[u][e] is the score given to entity e by user u
        - comparisons: DataFrame with columns
            * `user_id`
            * `criteria`
            * `entity_a`
            * `entity_b`
        
        Returns:
        - comparisons: DataFrame with columns
            * `user_id`
            * `criteria`
            * `score`
            * `entity_a`
            * `entity_b`
        """
        raise NotImplementedError

class GeneralizedBradleyTerry(ComparisonModel):
    """ The Generalized Bradley-Terry model is a score-to-comparison model
    with numerous desirable properties, which was introduced in the paper
    "Generalized Bradley-Terry Models for Score Estimation from Paired Comparisons"
    by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang and Oscar Villemaud,
    published at AAAI 2024.
    """
    
    @abstractmethod
    def sample_comparison(self, score_diff: float) -> float:
        raise NotImplementedError
    
    @abstractmethod
    def f(self, comparison: float) -> float:
        """ This is the function f in the paper.
        Depending on discrete/continuous, it may be the probability mass or density function.
        In our implementation, f does not need to correspond to a normalized probability.
        """
        raise NotImplementedError
    
    def non_normalized_probability(self, score_diff: float, comparison: float) -> float:
        return self.f(comparison) * np.exp(score_diff * comparison)
        
    @abstractmethod
    def partition_function(self, score_diff: float) -> float:
        raise NotImplementedError
    
    def probability(
        self, 
        score_diff: float, 
        comparison: float, 
        partition_fn: Optional[float] = None
    ) -> float:
        if partition_fn is None:
            partition_fn = self.partition_function(score_diff)
        return self.non_normalized_probability(score_diff, value) / partition_fn
    
class DiscreteGBT(GeneralizedBradleyTerry):
    def sample_comparison(self, score_diff: float) -> float:
        pf = self.root_law.partition_function(score_diff)
        cumulative = 0
        for comparison in self.comparison_generator():
            cumulative += self.probability(score_diff, comparison, pf)
            if rand <= cumulative:
                return comparison
        # Returns first comparison in case of numerical error
        return self.comparison_generator()
    
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
            total += self.non_normalized_probability(score_difference, comparison)
        return total

class KnaryGBT(DiscreteGBT):
    def __init__(self, n_options: int = 2, comparison_max: float = 1):
        """ n_options is k in the paper """
        assert (n_options >= 2) and (comparison_max > 0)
        self.n_options = n_options
        self.comparison_max = comparison_max

    def f(self, comparison: float) -> float:
        return 1

    def comparison_generator(self):
        delta = 2 * self.comparison_max / (self.n_options - 1)
        for k in range(self.n_options):
            yield k * delta - self.comparison_max

