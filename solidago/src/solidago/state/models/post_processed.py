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
        return self.post_process(self.parent(entity, criterion))

    def post_process(self, score: Union[Score, MultiScore]) -> Union[Score, MultiScore]:
        if isinstance(score, Score):
            value = self.post_process_fn(score.value)
            extremes = [self.post_process_fn(score.max), self.post_process_fn(score.min)]
            return Score(value, value - min(extremes), max(extremes) - value)
        else:
            return MultiScore({
                criterion: self.process(criterion_score)
                for criterion, criterion_score in score
            })


class SquashedModel(PostProcessedModel):
    def __init__(self, parent: ScoringModel, self.max_score: float=100.):
        super().__init__(parent)
        self.max_score = max_score
        
    def post_process_fn(self, x: float) -> float:
        return self.max_score * x / sqrt(1+x**2)

    def save(self, directory: Union[Path, str], filename: Optional[str], depth: int=0 ) -> tuple[str, Union[dict, str, tuple, list]]:
        parent_instructions = self.parent.save(directory, depth)
        return type(self).__name__, { 
            "parent": parent_instructions, 
            "args": { "max_score": self.max_score },
        }
