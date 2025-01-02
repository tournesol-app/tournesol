from typing import Optional, Union, Any
from pathlib import Path
from pandas import DataFrame, Series

from solidago.primitives.datastructure import NestedDictOfTuples
from .score import Score, MultiScore
from .base import ScoringModel, BaseModel


class DirectScoring(BaseModel, NestedDictOfTuples):
    def __init__(self,
        d: Optional[Union[NestedDictOfTuples, dict, DataFrame]]=None,
        key_names: list[str]=["entity_name", "criterion"], 
        value_names: list[str]=["score", "left_unc", "right_unc"],
        save_filename: Optional[str]=None
    ):
        """ Provides directly a MultiScore to scored entities """
        super().__init__(d, key_names, value_names, save_filename)

    def default_value(self) -> Score:
        return Score.nan()
    
    def process_stored_value(self, keys: list[str], stored_value: tuple[float, float, float]) -> Score:
        return Score(*stored_value)

    def score(self, entity: Union[str, "Entity"]) -> MultiScore:
        return MultiScore(self[str(entity)].to_df())

    @classmethod
    def args_load(cls, d: dict[str, Any], dfs: dict[str, DataFrame], depth: int) -> dict:
        if "directs" not in dfs:
            return dict()
        return dict(d=dfs["directs"][dfs["directs"]["depth"] == depth])
        
    def to_df(self, depth: int=0):
        return NestedDictOfTuples.to_df(self).assign(depth=depth)
