from abc import abstractmethod, ABC
from typing import Optional, Union
from pathlib import Path

import pandas as pd
import numpy as np


class Score:
    def __init__(
        self, 
        value: float=float("nan"), 
        left_uncertainty: float=float("inf"), 
        right_uncertainty: float=float("inf")
    ):
        self._value = value
        self._left_uncertainty = left_uncertainty
        self._right_uncertainty = right_uncertainty
    
    @property
    def value(self):
        return self._value

    @property
    def left(self):
        return self._left_uncertainty
        
    @property
    def right(self):
        return self._right_uncertainty
        
    @property
    def min(self):
        return self.value - self.left
    
    @property
    def max(self):
        return self.value + self.right
    
    def to_triplet(self):
        return self.value, self.left, self.right
    
    def average_uncertainty(self):
        return (self._left_uncertainty + self._right_uncertainty) / 2
    
    def __neg__(self):
        return Score(- self.value, self.right, self.left)
    
    def __add__(self, score: "Score"):
        return Score(
            self.value + score.value,
            self.left + score.left,
            self.right + score.right
        )
    
    def __mul__(self, s: "Score"):
        extremes = [ self.min * s.min, self.min * s.max, self.max * s.min, self.max * s.max ]
        value = self.value * score.value
        return Score(value, value - min(extremes), max(extremes) - value)
        
    def to_dict(self):
        return dict(value=self.value, left_uncertainty=self.left, right_uncertainty=self.right)
    
    def from_dict(d: dict):
        return Score(**d)
    
    def isnan(self):
        return self.value == float("nan") or (self.left == float("inf") and self.right == float("inf"))


class ScoringModel(ABC):
    def __call__(
        self, 
        entities: Union["Entity", "Entities"], 
        criteria: Optional[Union[list[str], str]]=None
    ) -> Union[Score, dict]:
        """ Assigns a score to an entity
        
        Parameters
        ----------
        entities: Union[Entity, Entities]
        criteria: Optional[str]
            
        Returns
        -------
        out: Score or dict
            If entities: Entity and criteria: str, the output is a Score.
            If entities: Entity and criteria is None or list, then out[criterion] is a Score.
            If entities: Entities and criteria: str, then out[entity] is a Score.
            If entities: Entity and criteria is None or list, then out[entity][criterion] is a Score.
        """
        from solidago.state.entities import Entity, Entities
        if isinstance(entities, Entities):
            return { entity: self(entity, criteria) for entity in entities }
        entity = entities
        if criteria is None:
            criteria = self.criteria()
        if isinstance(criteria, list):
            return { criterion: self(entity, criterion) for criterion in criteria }
        return self.score(entity, criteria)
        
    @classmethod
    def load(cls, instructions: dict, direct_model: "DirectScoring", scalings: dict, depth: int=0):
        import solidago.state.models as models
        base_cls, base_instr = instructions["base_model"]
        base_model = getattr(models, base_cls).load(base_instr, direct_model, scalings, depth + 1)
        return cls(base_model)

    @staticmethod
    def direct_scores_to_direct_model(direct_scores: pd.DataFrame) -> dict[str, "DirectScoring"]:
        """ Constructs a dict that maps username to DirectScoring """
        from solidago.state.models import DirectScoring, Score
        direct_model = DirectScoring()
        asymmetric = "left_unc" in direct_scores.columns
        left, right = ("left_unc", "right_unc") if asymmetric else ("uncertainty", "uncertainty")
        for _, r in direct_scores.iterrows():
            direct_model[r["entity_id"], r["criterion"]] = Score(r["score"], r[left], r[right])
        return direct_model

    @staticmethod
    def scalings_df_to_scaling_parameters(scalings_df: pd.DataFrame) -> dict:
        """ out[username][depth][criterion] yields the multiplicator and the translation (Score) """
        from solidago.state.models import Score
        scaling_params = dict()
        for _, r in scalings_df.iterrows():
            criterion, depth = r["criterion"], r["depth"]
            if depth not in scaling_params:
                scaling_params[depth] = dict()
            scaling_params[depth][criterion] = [
                Score(r["multiplicator_score"], r["multiplicator_left"], r["multiplicator_right"]),
                Score(r["translation_score"], r["translation_left"], r["translation_right"])
            ]
        return scaling_params
        
    @staticmethod
    def global_model_load(instructions: list, direct_scores: pd.DataFrame, scalings_df: pd.DataFrame=pd.DataFrame()):
        import solidago.state.models as models
        direct_model = ScoringModel.direct_scores_to_direct_model(direct_scores)
        scalings = ScoringModel.scalings_df_to_scaling_parameters(scalings_df)
        return getattr(models, instructions[0]).load(instructions[1], direct_model, scalings)
        
    @abstractmethod
    def save(self, filename: Union[Path, str]) -> Union[str, list, dict]:
        raise NotImplementedError
    
    @abstractmethod
    def score(self, entity: "Entity", criterion: str) -> Score:
        raise NotImplementedError

    @abstractmethod    
    def scored_entities(self, entities: "Entities", criterion: str) -> "Entities":
        """ Returned a subset of entities that are scored by the scoring model """
        raise NotImplementedError

    def from_dict(d: dict, entities: Optional["Entities"]=None):
        import solidago.state.models as models
        return getattr(models, d[0]).from_dict(d[1], entities)

    def __str__(self):
        return str(self.to_dict())
    
    def __repr__(self):
        return repr(self.to_dict())

    def save_scalings(self, filename: Union[Path, str]):
        filename = Path(filename)
        df = pd.DataFrame(columns=["criterion", "depth",
            "multiplicator_score", "multiplicator_left", "multiplicator_right", 
            "translation_score", "translation_left", "translation_right"])
        base_model, depth = model, 0
        while hasattr(base_model, "base_model"):
            if not isinstance(base_model, ScaledModel):
                continue
            for criterion in self.scaled_criteria():
                m = base_model.multiplicator(criterion)
                t = base_model.translation(criterion)
                df.iloc[-1] = [criterion, depth, m.value, m.left, m.right, t.value, t.left, t.right]
            depth += 1
            base_model = base_model.base_model
        df.to_csv(filename)
        return df
    
    def foundational_model(self, depth: int=0):
        return self.base_model.foundational_model(depth + 1) if hasattr(self, "base_model") else self, depth
    
