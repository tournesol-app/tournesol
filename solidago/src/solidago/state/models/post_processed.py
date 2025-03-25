from abc import abstractmethod
from typing import Optional, Callable, Union
from pathlib import Path
from math import sqrt
from pandas import DataFrame

from .score import Score, MultiScore
from .base import ScoringModel, DerivedModel


class PostProcessedModel(DerivedModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @abstractmethod
    def post_process_fn(self, x: float) -> float:
        """ This must be a monotonous function """
        raise NotImplemented
    
    def score(self, entity: "Entity", criterion: str) -> Score:
        return self.post_process(self.parent.score(entity, criterion))

    def post_process(self, score: Union[Score, MultiScore]) -> Union[Score, MultiScore]:
        if isinstance(score, Score):
            value = self.post_process_fn(score.value)
            extremes = [self.post_process_fn(score.max), self.post_process_fn(score.min)]
            return Score(value, value - min(extremes), max(extremes) - value)
        assert isinstance(score, MultiScore)
        return MultiScore(["criterion"], { c: self.post_process(s) for c, s in score })


class SquashedModel(PostProcessedModel):
    saved_argsnames: list[str]=["note", "score_max"]
    
    def __init__(self, parent: Union[ScoringModel, list, tuple], score_max: float=100., *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.score_max = score_max
        
    def post_process_fn(self, x: float) -> float:
        return self.score_max * x / sqrt(1+x**2)
