from abc import abstractmethod
from typing import Optional, Callable, Union
from pathlib import Path
from math import sqrt
from pandas import DataFrame

from .score import Score, MultiScore
from .base import ScoringModel


class PostProcessedModel(ScoringModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @abstractmethod
    def post_process_fn(self, x: float) -> float:
        """ This must be a monotonous function """
        raise NotImplemented
    
    def score(self, entity: "Entity") -> Union[Score, MultiScore]:
        return self.post_process(self.parent.score(entity))

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
    saved_argsnames: list[str]=["note", "max_score"]    
    
    def __init__(self, *args, max_score: float=100., **kwargs):
        super().__init__(*args, **kwargs)
        self.max_score = max_score
        
    def post_process_fn(self, x: float) -> float:
        return self.max_score * x / sqrt(1+x**2)
