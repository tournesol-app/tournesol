from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import numpy as np

class ComparisonModel(ABC):
    @abstractmethod
    def __call__(
        self, 
        users: pd.DataFrame, 
        entities: pd.DataFrame, 
        comparisons: pd.DataFrame
    ) -> pd.DataFrame:
        """ Fills in the comparisons
        
        Parameters
        ----------
        users: DataFrame
            Must have an index column `user_id`. May have others.
        entities: DataFrame with columns
            * `entity_id`: int
            * And maybe more
        comparisons: DataFrame with columns
            * `user_id`
            * `entity_a`
            * `entity_b`
        
        Returns
        -------
        comparisons: DataFrame with columns
            * `user_id`
            * `entity_a`
            * `entity_b`
            * `score`
        """
        raise NotImplementedError

    def __str__(self):
        return type(self).__name__

    def to_json(self):
        return (type(self).__name__, )
        
class GeneralizedBradleyTerry(ComparisonModel):
    """ The Generalized Bradley-Terry model is a score-to-comparison model
    with numerous desirable properties, which was introduced in the paper
    "Generalized Bradley-Terry Models for Score Estimation from Paired Comparisons"
    by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang and Oscar Villemaud,
    published at AAAI 2024.
    """
    def __init__(self, comparison_max: float=np.inf):
        assert comparison_max > 0
        self.comparison_max = comparison_max
    
    def __call__(
        self, 
        users: pd.DataFrame, 
        entities: pd.DataFrame, 
        comparisons: pd.DataFrame
    ) -> pd.DataFrame:
        """ Fills in the comparisons, using the Generalized Bradley-Terry model, see
        "Generalized Bradley-Terry Models for Score Estimation from Paired Comparisons"
        by Julien Fageot, Sadegh Farhadkhani, Lê-Nguyên Hoang and Oscar Villemaud,
        published at AAAI 2024.
        
        
        Parameters
        ----------
        users: DataFrame with columns
            * `user_id`: int, index
            * `n_comparisons`: float
            * `n_comparisons_per_entity`: float
        entities: DataFrame with columns
            * `entity_id`: int, index
        comparisons: DataFrame with columns
            * `user_id`
            * `entity_a`
            * `entity_b`
        
        Returns
        -------
        comparisons: DataFrame with columns
            * `user_id`
            * `entity_a`
            * `entity_b`
            * `comparison`
            * `comparison_max`
        """
        svd_dimension, svd_columns = 0, list()
        while True:
            column = f"svd{svd_dimension}"
            if column not in users or column not in entities:
                break
            svd_columns.append(column)
            svd_dimension += 1

        scores = users[svd_columns] @ entities[svd_columns].T / svd_dimension

        comparison_values = list()
        for _, row in comparisons.iterrows():
            user_vector = users.loc[row["user_id"], svd_columns]
            a_vector = entities.loc[row["entity_a"], svd_columns]
            b_vector = entities.loc[row["entity_b"], svd_columns]
            vector_diff = b_vector - a_vector
            score_diff = user_vector @ vector_diff / svd_dimension
            if "multiplicator" in users and np.isfinite(users.loc[row["user_id"], "multiplicator"]):
                score_diff *= users.loc[row["user_id"], "multiplicator"]
            if not users.loc[row["user_id"], "is_trustworthy"]:
                score_diff *= -1
            comparison_values.append(self.sample_comparison(score_diff))
        comparisons = comparisons.assign(comparison=comparison_values)
        comparison_max_list = [self.comparison_max] * len(comparisons)
        comparisons = comparisons.assign(comparison_max=comparison_max_list)
        return comparisons
    
    @abstractmethod
    def sample_comparison(self, score_diff: float) -> float:
        raise NotImplementedError
    
    @abstractmethod
    def root_law(self, comparison: float) -> float:
        """ This is the function f in the paper.
        Depending on discrete/continuous, it may be the probability mass or density function.
        In our implementation, f does not need to correspond to a normalized probability.
        """
        raise NotImplementedError
    
    def non_normalized_probability(self, score_diff: float, comparison: float) -> float:
        return self.root_law(comparison) * np.exp(score_diff * comparison)
    
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
        return self.non_normalized_probability(score_diff, comparison) / partition_fn
    
class DiscreteGBT(GeneralizedBradleyTerry):
    def __init__(self, comparison_max: float=np.inf):
        super().__init__(comparison_max)
        
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
