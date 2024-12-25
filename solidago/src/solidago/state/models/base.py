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
    def value(self) -> float:
        return self._value

    @property
    def left(self) -> float:
        return self._left_uncertainty
        
    @property
    def right(self) -> float:
        return self._right_uncertainty
        
    @property
    def min(self) -> float:
        return self.value - self.left
    
    @property
    def max(self) -> float:
        return self.value + self.right
    
    def to_triplet(self) -> tuple[float, float, float]:
        return self.value, self.left, self.right
    
    def average_uncertainty(self) -> float:
        return (self._left_uncertainty + self._right_uncertainty) / 2
    
    def __neg__(self) -> "Score":
        return Score(- self.value, self.right, self.left)
    
    def __add__(self, score: "Score") -> "Score":
        return Score(
            self.value + score.value,
            self.left + score.left,
            self.right + score.right
        )
    
    def __mul__(self, s: "Score") -> "Score":
        extremes = [ self.min * s.min, self.min * s.max, self.max * s.min, self.max * s.max ]
        value = self.value * score.value
        return Score(value, value - min(extremes), max(extremes) - value)

    def isnan(self) -> bool:
        return self.value == float("nan") or (self.left == float("inf") and self.right == float("inf"))


class ScoringModel(ABC):
    def __call__(self, 
        entities: Union["Entity", "Entities"], 
        criteria: Union["Criterion", "Criteria"]
    ) -> Union[Score, dict]:
        """ Assigns a score to an entity
        
        Parameters
        ----------
        entities: Union[Entity, Entities]
        criteria: Union[Criterion, Criteria]
            
        Returns
        -------
        out: Score or dict
            If entities: Entity and criteria: str, the output is a Score.
            If entities: Entity and criteria is None or list, then out[criterion_id] is a Score.
            If entities: Entities and criteria: str, then out[entity_id] is a Score.
            If entities: Entity and criteria is None or list, then out[entity_id][criterion_id] is a Score.
        """
        from solidago.state.entities import Entities
        from solidago.state.criteria import Criteria
        if isinstance(entities, Entities):
            return { entity: self(entity, criteria) for entity in entities }
        entity = entities
        if isinstance(criteria, Criteria):
            return { criterion: self(entity, criterion) for criterion in criteria }
        return self.score(entity, criteria)        
        
    @classmethod
    def load(cls, d: dict, direct_scores: DataFrame, scalings: dict, depth: int=0) -> "ScoringModel":
        import solidago.state.models as models
        base_cls, base_d = d["parent"]
        parent = getattr(models, base_cls).load(base_d, direct_scores, scalings, depth + 1)
        return cls(parent)

    @abstractmethod
    def save(self, filename: Union[Path, str]) -> tuple[str, Union[str, tuple, list, dict]]:
        raise NotImplementedError
    
    @abstractmethod
    def score(self, entity: "Entity", criterion: "Criterion") -> Score:
        raise NotImplementedError
    
    def base_model(self, depth: int=0) -> "BaseModel":
        return (self, depth) if isinstance(self, BaseModel) else self.parent.base_model(depth + 1)

    def from_dict(d: dict, entities: Optional["Entities"]=None) -> "ScoringModel":
        import solidago.state.models as models
        return getattr(models, d[0]).from_dict(d[1], entities)

    def __str__(self) -> str:
        return str(self.to_dict())
    
    def __repr__(self) -> str:
        return repr(self.to_dict())

    def save_scalings(self, filename: Optional[Union[Path, str]]) -> DataFrame:
        df = self.scalings_df()
        if filename is not None:
            df.to_csv(filename, index=False)
        return df

    def scalings_df(self) -> DataFrame:
        rows, parent, depth = list(), self, 0
        while not isinstance(parent, BaseModel):
            if not isinstance(parent, ScaledModel):
                continue
            for criterion in self.scaled_criteria():
                m = parent.multiplicator(criterion)
                t = parent.translation(criterion)
                rows.append([str(criterion), depth, m.value, m.left, m.right, t.value, t.left, t.right])
            depth += 1
            parent = parent.parent
        return DataFrame(rows, columns=["criterion_id", "depth",
            "multiplicator_score", "multiplicator_left", "multiplicator_right", 
            "translation_score", "translation_left", "translation_right"])
    
    def save_direct_scores(self, filename: Union[Path, str]) -> "ScoringModel":
        base_model, depth = self.base_model()
        from .direct import DirectScoring
        if isinstance(base_model, DirectScoring):
            base_model.save(filename, depth, save_scores=True)
        else:
            DataFrame().to_csv(filename)
        return self
    

class BaseModel(ScoringModel):
    @property
    def parent(self) -> ScoringModel:
        raise ValueError(f"{type(self)} is a BaseModel and thus has no parent")
