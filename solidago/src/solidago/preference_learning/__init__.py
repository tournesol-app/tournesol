from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import numpy as np

from solidago.solvers.optimize import brentq

class PreferenceLearning(ABC):
    @abstractmethod
    def __call__(
        self, 
        user_judgements: dict[str, pd.DataFrame],
        entities: pd.DataFrame
    ) -> ScoringModel:
        """ Learns a scoring model, given user judgements of entities
        
        Parameters
        ----------
        user_judgements: dict[str, pd.DataFrame]
            May contain different forms of judgements, 
            but most likely will contain "comparisons" and/or "assessments"
        entities: DataFrame with columns
            * entity_id: int, index
            * May contain others, such as vector representation
        """
        raise NotImplementedError


class ComparisonBasedPreferenceLearning(PreferenceLearning):
    @abstractmethod
    def comparison_learning(self, comparisons, entities) -> ScoringModel:
        """ Learns only based on comparisons
        
        Parameters
        ----------
        comparisons: DataFrame with columns
            * entity_a: int
            * entity_b: int
            * score: float
        entities: DataFrame with columns
            * entity_id: int, index
            * May contain others, such as vector representation
        """
        raise NotImplementedError
    
    def __call__(
        self, 
        user_judgements: dict[str, pd.DataFrame],
        entities: pd.DataFrame
    ) -> ScoringModel:
        return self.comparison_learning(user_judgements["comparisons"], entities)
    
    
