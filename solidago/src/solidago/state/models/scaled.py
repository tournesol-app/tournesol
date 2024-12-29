from typing import Union, Optional, Any
from pathlib import Path
from pandas import DataFrame

from solidago.primitives.datastructure.nested_dict import NestedDict
from .score import Score, MultiScore
from .base import ScoringModel


class ScaledModel(ScoringModel):
    def __init__(self, parent: ScoringModel, multiplicator: Score, translation: Score):
        super().__init__()
        self.parent = parent
        self.multiplicator = multiplicator
        self.translation = translation
    
    @classmethod
    def args_load(cls, d: dict[str, Any], dfs: dict[str, DataFrame], depth: int):
        depth_df = dfs["scalings"][dfs["scalings"]["depth"] == depth]
        if depth_df.empty:
            return dict(multiplicator=Score(1, 0, 0), translation=Score(0, 0, 0))
        if len(depth_df) > 1:
            logger.warn(f"Multiple scalings of same depth. Selected the last one.")
        r = depth_df.iloc[-1]
        return dict(
            multiplicator=Score(r["multiplicator_value"], r["multiplicator_left_unc"], r["multiplicator_right_unc"]), 
            translation=Score(r["translation_value"], r["translation_left_unc"], r["translation_right_unc"])
        )

    def score(self, entity: "Entity") -> Score:
        return self.scale( self.parent(entity) )

    def scale(self, score: Score) -> Score:
        return self.multiplicator * score + self.translation
    
    def set_scale(self, multiplicator: Score, translation: Score) -> None:
        self.multiplicator = multiplicator
        self.translation = translation
    
    def rescale(self, multiplicator: Score, translation: Score) -> None:
        self.multiplicator *= multiplicator
        self.translation = multiplicator * self.translation + translation
    
    def to_series_list(self, depth: int=0):
        return [Series(dict(
            depth=depth,
            multiplicator_value=self.multiplicator.value,
            multiplicator_left_unc=self.multiplicator.left_unc,
            multiplicator_right_unc=self.multiplicator.right_unc,
            translation_value=self.translation.value,
            translation_left_unc=self.translation.left_unc,
            translation_right_unc=self.translation.right_unc,
        ))]
        
    def to_df(self, depth: int=0):
        return DataFrame(self.to_series_list(depth))
    
    def to_series_list(self, depth):
        raise NotImplementedError


class MultiScaledModel(ScoringModel, NestedDict):
    def __init__(self,
        parent: ScoringModel,
        d: Optional[Union[NestedDict, dict, DataFrame]]=None,
        key_names: list[str]=["criterion"], 
        value_names: Optional[list[str]]=None,
        save_filename: Optional[str]=None
    ):
        super().__init__(d, key_names, value_names, save_filename)
        self.parent = parent

    def default_value(self) -> tuple[Score, Score]:
        return Score(1, 0, 0), Score(0, 0, 0)
    
    def value_process(self, value: Any, keys: Optional[list]=None) -> tuple[Score, Score]:
        if isinstance(value, (tuple, list)) and len(value) == 2:
            return Score(value[0]), Score(value[1])
        if isinstance(value, (dict, Series)) and len(value) == 2:
            return (
                Score(value["multiplicator_value"], value["multiplicator_left_unc"], value["multiplicator_right_unc"]), 
                Score(value["translation_value"], value["translation_left_unc"], value["translation_right_unc"]), 
            )
        return value

    def values2list(self, value: Any) -> list:
        return list(value[0].to_triplet()) + list(value[1].to_triplet())

    @classmethod
    def args_load(cls, d: dict[str, Any], dfs: dict[str, DataFrame], depth: int) -> dict:
        depth_df = dfs["scalings"][dfs["scalings"]["depth"] == depth]
        if depth_df.empty:
            return dict(multiplicator=Score(1, 0, 0), translation=Score(0, 0, 0))
        d = dict()
        for _, r in depth_df.iterrows():
            if r["criterion"] in d:
                logger.warn(f"Multiple scalings of same depth with same criterion. Selected the last one.")
            d[r["criterion"]] = (
                Score(r["multiplicator_value"], r["multiplicator_left_unc"], r["multiplicator_right_unc"]),
                Score(r["translation_value"], r["translation_left_unc"], r["translation_right_unc"]),
            )
        return dict(d=d)

    @property
    def multiplicator(self) -> MultiScore:
        return MultiScore({ criterion: value[0] for criterion, value in self })
        
    @multiplicator.setter
    def multiplicator(self, value: MultiScore) -> None:
        for criterion, m in value:
            self[criterion] = m, self[criterion][1]
        
    @property
    def translation(self) -> MultiScore:
        return MultiScore({ criterion: value[1] for criterion, value in self })
        
    @translation.setter
    def translation(self, value: MultiScore) -> None:
        for criterion, t in value:
            self[criterion] = self[criterion][1], t
    
    def score(self, entity: "Entity") -> MultiScore:
        return self.scale( self.parent(entity) )

    def scale(self, score: MultiScore) -> MultiScore:
        return self.multiplicator * score + self.translation
    
    def set_scale(self, multiplicator: Score, translation: Score, criterion: str) -> None:
        self[criterion] = multiplicator, translation
    
    def rescale(self, multiplicator: Score, translation: Score) -> None:
        self.multiplicator *= multiplicator
        self.translation = multiplicator * self.translation + translation

