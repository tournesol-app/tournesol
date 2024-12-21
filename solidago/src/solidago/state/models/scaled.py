from typing import Union
from pathlib import Path

import pandas as pd

from .base import Score, ScoringModel


class ScaledModel(ScoringModel):
    def __init__(self, base_model: ScoringModel, scaling_parameters: dict=dict()):
        self.base_model = base_model
        self.scaling_parameters = scaling_parameters
        self.iterator = None
    
    @classmethod
    def load(cls, instructions: dict, entities: "Entities", direct_scores: pd.DataFrame, scalings: pd.DataFrame, depth: int=0):
        import solidago.state.models as models
        base_model = getattr(models, instructions["base_model"][0]).load(
            instructions["base_model"][1], entities, direct_scores, scalings, depth+1)
        model = cls(base_model)
        for criterion in instructions["scaling_parameters"]:
            params = { "multiplicator": Score(1, 0, 0), "translation": Score(0, 0, 0) }
            for key, value in instructions["scaling_parameters"][criterion].items():
                params[key] = Score(value[0], value[1], value[2])
            model.rescale(criterion, params["multiplicator"], params["translation"])
        return model

    def save(self, directory: Union[Path, str], filename: str="scores", depth: int=0) -> Union[str, list, dict]:
        base_model_instructions = self.base_model.save(directory, depth)
        return [self.__class__.__name__, {
            "base_model": base_model_instructions,
            "scaling_parameters": {
                criterion: {
                    "multiplicator": [
                        self.scaling_parameters[criterion][0].value,
                        self.scaling_parameters[criterion][0].left,
                        self.scaling_parameters[criterion][0].right                        
                    ],
                    "translation": [
                        self.scaling_parameters[criterion][1].value,
                        self.scaling_parameters[criterion][1].left,
                        self.scaling_parameters[criterion][1].right                        
                    ],
                } for criterion in self.scaled_criteria()
            }
        }]

    def score(self, entity: "Entity", criterion: str):
        score = self.base_model(entity, criterion)
        return None if score is None else self.scale(score, criterion)

    def scale(self, score: Score, criterion: str) -> Score:
        return self.multiplicator(criterion) * score + self.translation(criterion)
    
    def rescale(self, criterion: str, multiplicator: Score, translation: Score):
        if criterion not in self.scaling_parameters:
            self.scaling_parameters[criterion] = (multiplicator, translation)
        else:
            self.scaling_parameters[criterion][0] *= multiplicator
            self.scaling_parameters[criterion][1] *= multiplicator 
            self.scaling_parameters[criterion][1] += translation
    
    def scaled_criteria(self):
        return list(self.scaling_paramters.keys())
    
    def multiplicator(self, criterion: str) -> Score:
        if criterion not in self.scaling_parameters:
            return Score(1, 0, 0)
        return self.scaling_parameters[criterion][0]
        
    def translation(self, criterion: str) -> Score:
        if criterion not in self.scaling_parameters:
            return Score(0, 0, 0)
        return self.scaling_parameters[criterion][1]
    
    def set_multiplicator(self, criterion: str, multiplicator: Score):
        if criterion not in self.scaling_parameters:
            self.scaling_parameters[criterion] = (multiplicator, Score(0, 0, 0))
        else:
            self.scaling_parameters[criterion][0] = multiplicator
    
    def set_translation(self, criterion: str, translation: Score):
        if criterion not in self.scaling_parameters:
            self.scaling_parameters[criterion] = (Score(1, 0, 0), translation)
        else:
            self.scaling_parameters[criterion][1] = translation
    
    def scored_entities(self, entities: "Entities", criterion: str) -> "Entities":
        return self.base_model.scored_entities(entities, criterion)
        
    def to_dict(self, data=False):
        return [self.__class__.__name__, dict() if not data else { 
            "base_model": self.base_model.to_dict(data=True),
            "scaling_parameters": {
                criterion: {
                    "multiplicator": self.multiplicator(criterion).to_triplet(),
                    "translation": self.translation(criterion).to_triplet()
                } for criterion, values in self.scaling_parameters.items()
            }
        }]
    
    @classmethod
    def from_dict(self, d: dict, pd_scaling: pd.DataFrame, pd_direct_scores: pd.DataFrame):
        return ScaledModel(
            base_model=ScoringModel.from_dict(d["base_model"], entities),
            scaling_parameters={
                criterion: {
                    "multiplicator": Score(*value["multiplicator"]),
                    "translation": Score(*value["translation"])
                } for criterion, value in d["scaling_parameters"].items()
            }
        )
