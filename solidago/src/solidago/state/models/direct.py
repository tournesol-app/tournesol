from typing import Optional, Union, Any
from pathlib import Path
from pandas import DataFrame, Series

from solidago.primitives.datastructure.nested_dict import NestedDict
from .score import Score, MultiScore
from .base import ScoringModel, BaseModel


class DirectScoring(BaseModel, NestedDict):
    def __init__(self,
        d: Optional[Union[NestedDict, dict, DataFrame]]=None,
        key_names: list[str]=["entity_name"], 
        value_names: Optional[list[str]]=["score", "left_unc", "right_unc"],
        save_filename: Optional[str]=None
    ):
        """ Provides directly a Score to scored entities """
        super().__init__(d, key_names, value_names, save_filename)

    def default_value(self) -> Score:
        return Score.nan()
    
    def value_process(self, value, keys: Optional[list]=None) -> Score:
        if isinstance(value, Score):
            return value
        elif isinstance(value, (tuple, list)):
            return Score(*value)
        return Score(*[value[name] for name in self.value_names])

    def values2list(self, value: Score) -> list:
        return list(value.to_triplet())

    def score(self, entity: Union[str, "Entity"]) -> Score:
        return self[str(entity)]  

    @classmethod
    def args_load(cls, d: dict[str, Any], dfs: dict[str, DataFrame], depth: int) -> dict:
        return dict(d=dfs["directs"][dfs["directs"]["depth"] == depth])
        
    def to_series_list(self, depth: int=0):
        return [
            Series(score.to_dict() | dict(entity_name=entity_name, depth=depth) ) 
            for entity_name, score in self
        ]
        
    def to_df(self, depth: int=0):
        return DataFrame(self.to_series_list(depth))
    

class DirectMultiScoring(BaseModel, NestedDict):
    def __init__(self,
        d: Optional[Union[NestedDict, dict, DataFrame]]=None,
        key_names: list[str]=["entity_name", "criterion"], 
        value_names: Optional[list[str]]=["score", "left_unc", "right_unc"],
        save_filename: Optional[str]=None
    ):
        """ Provides directly a MultiScore to scored entities """
        super().__init__(d, key_names, value_names, save_filename)

    def default_value(self) -> MultiScore:
        return MultiScore.nan()
    
    def value_process(self, value, keys: Optional[list]=None) -> MultiScore:
        result = MultiScore() if keys is None else self[keys]
        if isinstance(value, MultiScore):
            return result | value
        elif isinstance(value, (dict, Series, NestedDict)) and "criterion" in value:
            result[value["criterion"]] = Score(value["score"], value["left_unc"], value["right_unc"])
            return result
        elif isinstance(value, (dict, Series, NestedDict)):
            for criterion, score in value.items():
                result[criterion] = Score(score)
            return result
        return result | MultiScore(value)
        
    def score(self, entity: Union[str, "Entity"]) -> MultiScore:
        return self[str(entity)]

    @classmethod
    def args_load(cls, d: dict[str, Any], dfs: dict[str, DataFrame], depth: int) -> dict:
        if "directs" not in dfs:
            return dict()
        return dict(d=dfs["directs"][dfs["directs"]["depth"] == depth])

    def to_dict(self, keys: list[str], value: NestedDict) -> list[dict]:
        keys_dict = self.keys2dict(keys)
        return [
            keys_dict | { "criterion": criterion } | score.to_dict()
            for criterion, score in value
        ]
    
    def save(self, filename: Union[Path, str]) -> tuple[str, str]:
        NestedDict.self.save(filename)

    def to_series_list(self, depth: int=0) -> list[Series]:
        return [
            Series(score.to_dict() | dict(entity_name=entity_name, criterion=criterion, depth=depth) ) 
            for entity_name, score in self
            for criterion in self[entity_name]
        ]
        
    def to_df(self, df_name: str="directs", depth: int=0) -> DataFrame:
        return DataFrame(self.to_series_list(depth))
