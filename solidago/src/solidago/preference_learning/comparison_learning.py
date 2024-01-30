from abc import abstractmethod
from typing import Optional
import pandas as pd

from solidago.scoring_model import ScoringModel

from .base import PreferenceLearning


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
    
    def user_learn(
        self, 
        user_judgments: dict[str, pd.DataFrame],
        entities: pd.DataFrame,
        initialization: Optional[ScoringModel] = None
    ) -> ScoringModel:
        """ Learns a scoring model, given user judgments of entities
        
        Parameters
        ----------
        user_judgments: dict[str, pd.DataFrame]
            May contain different forms of judgments, 
            but most likely will contain "comparisons" and/or "assessments"
        entities: DataFrame with columns
            * entity_id: int, index
            * May contain others, such as vector representation
        initialization: ScoringModel or None
            Starting model, added to facilitate optimization
            It is not supposed to affect the output of the training
            
        Returns
        -------
        model: ScoringModel
        """
        return self.comparison_learning(user_judgments["comparisons"], entities, initialization)
