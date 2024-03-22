from abc import abstractmethod
from typing import Optional
import pandas as pd

from solidago.scoring_model import ScoringModel

from .base import PreferenceLearning


class ComparisonBasedPreferenceLearning(PreferenceLearning):
    @abstractmethod
    def comparison_learning(
        self, 
        comparisons: pd.DataFrame, 
        entities: pd.DataFrame, 
        initialization: Optional[ScoringModel]=None, 
        updated_entities: Optional[set[int]]=None,
    ) -> ScoringModel:
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
        initialization: ScoringModel or None
            Starting model, added to facilitate optimization
            It is not supposed to affect the output of the training
        updated_entities: set of entities (int)
           This allows to prioritize coordinate descent, starting with newly evaluated entities
        """
        raise NotImplementedError
    
    def user_learn(
        self, 
        user_judgments: dict[str, pd.DataFrame],
        entities: pd.DataFrame,
        initialization: Optional[ScoringModel] = None,
        new_judgments: Optional[dict[str, pd.DataFrame]]=None,  # TODO: should use Judgements ?
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
        new_judgments: New judgments
           This allows to prioritize coordinate descent, starting with newly evaluated entities
            
        Returns
        -------
        model: ScoringModel
        """
        comparisons, updated_entities = user_judgments["comparisons"], None
        if new_judgments is not None:
            new_comparisons = new_judgments["comparisons"]
            updated_entities = set(new_comparisons["entity_a"]) | set(new_comparisons["entity_b"])
        return self.comparison_learning(comparisons, entities, initialization, updated_entities)
