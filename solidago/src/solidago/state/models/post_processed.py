from abc import abstractmethod
from typing import Optional, Callable, Union
from pathlib import Path
from math import sqrt
from pandas import DataFrame

from .score import Score, MultiScore
from .base import ScoringModel


class PostProcessedModel(ScoringModel):
    def __init__(self, parent: ScoringModel):
        """ Abstract class that defines a derived scoring model, by post-processing the outputs
        of a base model """
        self.parent = parent
    
    @abstractmethod
    def post_process_fn(self, x: float) -> float:
        """ This must be a monotonous function """
        raise NotImplemented
    
    def score(self, entity: "Entity") -> Union[Score, MultiScore]:
        return self.post_process(self.parent(entity))

    def post_process(self, score: Union[Score, MultiScore]) -> Union[Score, MultiScore]:
        if isinstance(score, Score):
            value = self.post_process_fn(score.value)
            extremes = [self.post_process_fn(score.max), self.post_process_fn(score.min)]
            return Score(value, value - min(extremes), max(extremes) - value)
        assert isinstance(score, MultiScore)
        return MultiScore({
            criterion: self.post_process(criterion_score)
            for criterion, criterion_score in score
        })


class SquashedModel(PostProcessedModel):
    def __init__(self, parent: ScoringModel, max_score: float=100.):
        super().__init__(parent)
        self.max_score = max_score
        
    def post_process_fn(self, x: float) -> float:
        return self.max_score * x / sqrt(1+x**2)

    def save(self, 
        directory: Optional[Union[Path, str]]=None, 
        depth: int=0
    ) -> tuple[str, dict]:
        return type(self).__name__, { 
            "parent": self.parent.save(directory, depth + 1), 
            "args": { "max_score": self.max_score },
        }
