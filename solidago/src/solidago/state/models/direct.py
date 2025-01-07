from typing import Optional, Union, Any
from pathlib import Path
from pandas import DataFrame, Series

from .score import Score, MultiScore
from .base import ScoringModel, BaseModel


class DirectScoring(BaseModel, MultiScore):
    def __init__(self,
        d: Optional[Union[MultiScore, dict, DataFrame]]=None,
        key_names: list[str]=["entity_name", "criterion"], 
        value_names: list[str]=["score", "left_unc", "right_unc"],
        save_filename: Optional[str]=None
    ):
        """ Provides directly a MultiScore to scored entities """
        super().__init__(d, key_names, value_names, save_filename)

    def to_direct(self, entities: Optional["Entities"]=None) -> "DirectScoring":
        return self
        
    def score(self, entity: Union[str, "Entity"]) -> MultiScore:
        return self[str(entity)]

    def evaluated_entities(self, entities: "Entities") -> "Entities":
        return entities.get(self.get_set("entity_name"))
        
    @classmethod
    def args_load(cls, d: dict[str, Any], dfs: dict[str, DataFrame], depth: int) -> dict:
        if "directs" not in dfs:
            return dict()
        if "depth" not in dfs["directs"]:
            return dict(d=dfs["directs"])
        return dict(d=dfs["directs"][dfs["directs"]["depth"] == depth])

    def to_rows(self, depth: int=0, kwargs: Optional[dict]=None) -> dict[str, list]:
        kwargs = dict() if kwargs is None else kwargs
        return dict(directs=MultiScore.to_rows(self, kwargs | dict(depth=depth)))
    
    def to_df(self, depth: int=0) -> DataFrame:
        return DataFrame(self.to_rows(depth)["directs"])
        
    def __repr__(self) -> str:
        return MultiScore.__repr__(self)
