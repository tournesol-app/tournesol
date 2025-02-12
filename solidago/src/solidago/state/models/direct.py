from typing import Optional, Union, Any
from pathlib import Path
from pandas import DataFrame, Series

from .score import Score, MultiScore
from .base import ScoringModel, BaseModel


class DirectScoring(ScoringModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "directs" not in self.dfs:
            self.dfs["directs"] = MultiScore(key_names=["entity_name", "criterion"])

    def score(self, entity: Union[str, "Entity"]) -> MultiScore:
        return self.dfs["directs"].get(entity)
        
    def to_direct(self, entities: Optional["Entities"]=None) -> "DirectScoring":
        return self

    def evaluated_entities(self, entities: "Entities") -> "Entities":
        return entities.get(set(self["entity_name"]))
        
    def __repr__(self) -> str:
        return repr(self.dfs["directs"])
