from typing import Union, Optional, Any
from pathlib import Path
from pandas import DataFrame

from solidago.primitives.datastructure import NestedDictOfTuples
from .score import Score, MultiScore
from .base import ScoringModel


class ScaledModel(ScoringModel):
    def __init__(self, 
        parent: ScoringModel, 
        multiplicator: Score=Score(1, 0, 0), 
        translation: Score=Score(0, 0, 0)
    ):
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

    def score(self, entity: "Entity") -> MultiScore:
        return self.scale( self.parent(entity) )

    def scale(self, score: Union[Score, MultiScore]) -> Union[Score, MultiScore]:
        return score * self.multiplicator + self.translation
    
    def set_scale(self, multiplicator: Score, translation: Score) -> None:
        self.multiplicator = multiplicator
        self.translation = translation
    
    def rescale(self, multiplicator: Score, translation: Score) -> None:
        self.multiplicator *= multiplicator
        self.translation = multiplicator * self.translation + translation
    
    def to_row_list(self, depth: int=0) -> list[dict]:
        return [dict(
            depth=depth,
            multiplicator_value=self.multiplicator.value,
            multiplicator_left_unc=self.multiplicator.left_unc,
            multiplicator_right_unc=self.multiplicator.right_unc,
            translation_value=self.translation.value,
            translation_left_unc=self.translation.left_unc,
            translation_right_unc=self.translation.right_unc,
        )]
        
    def to_df(self, depth: int=0) -> DataFrame:
        return DataFrame(self.to_row_list(depth))


class MultiScaledModel(ScoringModel, NestedDictOfTuples):
    def __init__(self,
        parent: ScoringModel,
        d: Optional[Union[NestedDictOfTuples, dict, DataFrame]]=None,
        key_names: list[str]=["criterion"], 
        value_names: list[str]=[
            "multiplicator_value", "multiplicator_left_unc", "multiplicator_right_unc", 
            "translation_value", "translation_left_unc", "translation_right_unc",
        ],
        save_filename: Optional[str]=None
    ):
        super().__init__(d, key_names, value_names, save_filename)
        self.parent = parent

    def default_value(self) -> tuple[Score, Score]:
        return Score(1, 0, 0), Score(0, 0, 0)
    
    def process_stored_value(self, 
        keys: list[str], 
        stored_value: tuple[float, float, float, float, float, float]
    ) -> tuple[Score, Score]:
        return Score(*stored_value[0:3]), Score(*stored_value[3:6])

    @classmethod
    def args_load(cls, d: dict[str, Any], dfs: dict[str, DataFrame], depth: int) -> dict:
        depth_df = dfs["scalings"][dfs["scalings"]["depth"] == depth]
        return dict(d=depth_df)

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

