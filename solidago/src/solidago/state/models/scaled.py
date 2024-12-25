from typing import Union, Optional
from pathlib import Path
from pandas import DataFrame

from .base import Score, ScoringModel


class ScaledModel(ScoringModel):
    def __init__(self, parent: ScoringModel, scaling_parameters: Optional[dict]=None):
        self.parent = parent
        self.scaling_parameters = dict() if scaling_parameters is None else scaling_parameters

    @classmethod
    def load(cls, d: dict, direct_scores: DataFrame, scalings: dict, depth: int=0) -> "ScaledModel":
        import solidago.state.models as models
        base_cls, base_d = d["parent"]
        parent = getattr(models, base_cls).load(base_d, direct_scores, scalings, depth + 1)
        model = cls(parent)
        for criterion_id, scaling_params in scalings[depth].items():
            model.rescale(criterion_id, scaling_params[0], scaling_params[1])
        return model

    def save(self, directory: Union[Path, str], filename: str="scores", depth: int=0) -> Union[str, list, dict]:
        parent_instructions = self.parent.save(directory, depth)
        return [self.__class__.__name__, parent_instructions]

    def score(self, entity: "Entity", criterion: "Criterion") -> Score:
        score = self.parent(entity, criterion)
        return None if score is None else self.scale(score, criterion)

    def scale(self, score: Score, criterion: "Criterion") -> Score:
        return self.multiplicator(criterion) * score + self.translation(criterion)
    
    def set_scale(self, criterion: "Criterion", multiplicator: Score, translation: Score) -> "ScaledModel":
        self.scaling_parameters[str(criterion)] = (multiplicator, translation)
        return self
    
    def rescale(self, criterion: "Criterion", multiplicator: Score, translation: Score) -> "ScaledModel":
        if str(criterion) not in self.scaling_parameters:
            self.scaling_parameters[str(criterion)] = (multiplicator, translation)
        else:
            self.scaling_parameters[str(criterion)][0] *= multiplicator
            self.scaling_parameters[str(criterion)][1] *= multiplicator 
            self.scaling_parameters[str(criterion)][1] += translation
        return self
    
    def scaled_criteria(self) -> "Criteria":
        from solidago.state import Criteria
        return Criteria(dict(criterion_id=list(self.scaling_paramters.keys())))
    
    def multiplicator(self, criterion: "Criterion") -> Score:
        if str(criterion) not in self.scaling_parameters:
            return Score(1, 0, 0)
        return self.scaling_parameters[criterion][0]
        
    def translation(self, criterion: "Criterion") -> Score:
        if str(criterion) not in self.scaling_parameters:
            return Score(0, 0, 0)
        return self.scaling_parameters[str(criterion)][1]
    
    def set_multiplicator(self, criterion: "Criterion", multiplicator: Score) -> "ScaledModel":
        if str(criterion) not in self.scaling_parameters:
            self.scaling_parameters[str(criterion)] = (multiplicator, Score(0, 0, 0))
        else:
            self.scaling_parameters[str(criterion)][0] = multiplicator
        return self
    
    def set_translation(self, criterion: "Criterion", translation: Score) -> "ScaledModel":
        if str(criterion) not in self.scaling_parameters:
            self.scaling_parameters[str(criterion)] = (Score(1, 0, 0), translation)
        else:
            self.scaling_parameters[str(criterion)][1] = str(translation)
        return self
        
    def to_dict(self, data=False) -> tuple[str, dict]:
        return [self.__class__.__name__, dict() if not data else { 
            "parent": self.parent.to_dict(data=True),
            "scaling_parameters": {
                criterion_id: {
                    "multiplicator": self.multiplicator(criterion).to_triplet(),
                    "translation": self.translation(criterion).to_triplet()
                } for criterion_id, values in self.scaling_parameters.items()
            }
        }]
    
    @classmethod
    def from_dict(self, d: dict, scaling_df: DataFrame, direct_scores_df: DataFrame) -> "ScaledModel":
        return ScaledModel(
            parent=ScoringModel.from_dict(d["parent"], entities),
            scaling_parameters={
                criterion_id: {
                    "multiplicator": Score(*value["multiplicator"]),
                    "translation": Score(*value["translation"])
                } for criterion_id, value in d["scaling_parameters"].items()
            }
        )
