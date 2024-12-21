from typing import Optional, Callable, Union
from pathlib import Path
from math import sqrt

import pandas as pd

from .base import Score, ScoringModel


class PostProcessedModel(ScoringModel):
    def __init__(self, base_model: ScoringModel, post_process_fn: Callable):
        """ Defines a derived scoring model, based on a base model and a post process
        
        Parameters
        ----------
        base_model: ScoringModel
        post_process_fn: callable
            Must be a monotonous function float -> float
        """
        self.base_model = base_model
        self.post_process_fn = post_process_fn
    
    def score(self, entity: "Entity", criterion: str):
        score = self.base_model(entity, criterion)
        return None if score is None else self.post_process(score)

    def post_process(self, score: Score):
        value = self.post_process_fn(score.value)
        extremes = [self.post_process_fn(score.max), self.post_process_fn(score.min)]
        return Score(value, value - min(extremes), max(extremes) - value)

    def scored_entities(self, entities: Optional["Entities"], criterion: Optional[str]) -> "Entities":
        return self.base_model.scored_entities(entities, criterion)


class SquashedModel(PostProcessedModel):
    def __init__(self, base_model: ScoringModel):
        super().__init__(base_model, lambda x: 100 * x / sqrt(1+x**2))
        
    def to_dict(self):
        return [self.__class__.__name__, { "base_model": self.base_model.to_dict() }]
    
    def from_dict(self, d: dict, entities: "Entities"):
        return SquashedModel(ScoringModel.from_dict(d["base_model"], entities))

    def save(self, directory: Union[Path, str], filename: str="scores", depth: int=0) -> Union[str, list, dict]:
        base_model_instructions = self.base_model.save(directory, depth)
        return [self.__class__.__name__, { "base_model": base_model_instructions }]
        
    def to_dict(self, data=False):
        return [self.__class__.__name__, dict() if not data else { 
            "base_model": self.base_model.to_dict(data=True)
        }]
    
    @classmethod
    def from_dict(self, d: dict, pd_scaling: pd.DataFrame, pd_direct_scores: pd.DataFrame):
        return ScaledModel(
            base_model=ScoringModel.from_dict(d["base_model"], entities),
            multiplicator=Score.from_dict(d["multiplicator"]),
            translation=Score.from_dict(d["translation"])
        )
