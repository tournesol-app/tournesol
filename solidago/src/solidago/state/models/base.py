from abc import abstractmethod, ABC
from typing import Optional, Union
from pathlib import Path
from pandas import DataFrame


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
        if isinstance(criteria, (int, str)):
            return self.score(entity, criteria)
        if criteria is None:
            criteria = self.criteria()
        return { criterion: self(entity, criterion) for criterion in criteria }
        
    @classmethod
    def load(cls, d: dict, direct_scores: DataFrame, scalings: dict, depth: int=0):
        import solidago.state.models as models
        base_cls, base_d = d["base_model"]
        base_model = getattr(models, base_cls).load(base_d, direct_scores, scalings, depth + 1)
        return cls(base_model)

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
        df = self.scalings_df()
        df.to_csv(filename)
        return df

    def scalings_df(self):
        rows, base_model, depth = list(), self, 0
        while hasattr(base_model, "base_model"):
            if not isinstance(base_model, ScaledModel):
                continue
            for criterion in self.scaled_criteria():
                m = base_model.multiplicator(criterion)
                t = base_model.translation(criterion)
                rows.append([criterion, depth, m.value, m.left, m.right, t.value, t.left, t.right])
            depth += 1
            base_model = base_model.base_model
        return DataFrame(rows, columns=["criterion", "depth",
            "multiplicator_score", "multiplicator_left", "multiplicator_right", 
            "translation_score", "translation_left", "translation_right"])
        
    
    def save_direct_scores(self, filename: Union[Path, str]):
        foundation_model, depth = self.foundational_model()
        from .direct import DirectScoring
        if isinstance(foundation_model, DirectScoring):
            foundation_model.save(filename, depth, save_scores=True)
        else:
            DataFrame().to_csv(filename)
    
    def foundational_model(self, depth: int=0):
        return self.base_model.foundational_model(depth + 1) if hasattr(self, "base_model") else (self, depth)
    
