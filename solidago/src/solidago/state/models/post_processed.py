from typing import Optional, Callable, Union
from pathlib import Path
from math import sqrt
from pandas import DataFrame

from .base import Score, ScoringModel


class PostProcessedModel(ScoringModel):
    def __init__(self, parent: ScoringModel, post_process_fn: Callable):
        """ Defines a derived scoring model, based on a base model and a post process
        
        Parameters
        ----------
        parent: ScoringModel
        post_process_fn: callable
            Must be a monotonous function float -> float
        """
        self.parent = parent
        self.post_process_fn = post_process_fn
    
    def score(self, entity: "Entity", criterion: "Criterion") -> Score:
        return self.post_process(self.parent(entity, criterion))

    def post_process(self, score: Score) -> Score:
        value = self.post_process_fn(score.value)
        extremes = [self.post_process_fn(score.max), self.post_process_fn(score.min)]
        return Score(value, value - min(extremes), max(extremes) - value)


class SquashedModel(PostProcessedModel):
    def __init__(self, parent: ScoringModel):
        super().__init__(parent, lambda x: 100 * x / sqrt(1+x**2))
        
    def to_dict(self) -> tuple[str, dict]:
        return [self.__class__.__name__, { "parent": self.parent.to_dict() }]
    
    def from_dict(self, d: dict, entities: "Entities") -> "SquashedModel":
        return SquashedModel(ScoringModel.from_dict(d["parent"], entities))

    def save(self, directory: Union[Path, str], filename: str, depth: int=0 ) -> tuple[str, Union[dict, str, tuple, list]]:
        parent_instructions = self.parent.save(directory, depth)
        return [self.__class__.__name__, { "parent": parent_instructions }]
        
    def to_dict(self, data=False) -> tuple[str, dict]:
        return [self.__class__.__name__, dict() if not data else { 
            "parent": self.parent.to_dict(data=True)
        }]
    
    @classmethod
    def from_dict(self, d: dict, scaling_df: DataFrame, direct_scores_df: DataFrame) -> "SquashedModel":
        return SquashedModel(ScoringModel.from_dict(d["parent"], entities))
