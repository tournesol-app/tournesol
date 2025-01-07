from typing import Union, Optional, Any
from pathlib import Path
from pandas import DataFrame

from solidago.primitives.datastructure import NestedDictOfTuples
from .score import Score, MultiScore
from .base import ScoringModel


class ScaleDict(NestedDictOfTuples):
    def __init__(self,
        d: Optional[Union[NestedDictOfTuples, dict, DataFrame]]=None,
        key_names: list[str]=["criterion"], 
        value_names: list[str]=[
            "multiplicator_value", "multiplicator_left_unc", "multiplicator_right_unc", 
            "translation_value", "translation_left_unc", "translation_right_unc",
        ],
        save_filename: Optional[str]=None
    ):
        super().__init__(d, key_names, value_names, save_filename)

    def default_value(self) -> tuple[Score, Score]:
        return Score(1, 0, 0), Score(0, 0, 0)
    
    def process_stored_value(self, 
        keys: list[str], 
        stored_value: tuple[float, float, float, float, float, float]
    ) -> tuple[Score, Score]:
        return Score(*stored_value[0:3]), Score(*stored_value[3:6])


class ScaledModel(ScoringModel):
    def __init__(self,
        parent: ScoringModel,
        scales: Optional[ScaleDict]=None,
        note: str="None"
    ):
        self.parent = parent
        self.scales = scales
        self.note = note

    @classmethod
    def args_load(cls, d: dict[str, Any], dfs: dict[str, DataFrame], depth: int) -> dict:
        scales_df = dfs["scalings"][dfs["scalings"]["depth"] == depth]
        return super().args_load(d, dfs, depth) | dict(scales=ScaleDict(scales_df))

    def args_save(self) -> dict:
        return dict(note=self.note)

    def to_rows(self, depth: int=0, kwargs: Optional[dict]=None) -> dict[str, list]:
        kwargs = dict() if kwargs is None else kwargs
        self_rows = dict(scalings=self.scales.to_rows(kwargs | dict(depth=depth)))
        parent_rows = self.parent.to_rows(depth + 1, kwargs)
        get = lambda rows, key: rows[key] if key in rows else list()
        return {
            key: get(self_rows, key) + get(parent_rows, key)
            for key in set(self_rows) | set(parent_rows)
        }
        
    @property
    def multiplicator(self) -> MultiScore:
        return MultiScore({ criterion: value[0].to_triplet() for criterion, value in self.scales })
        
    @multiplicator.setter
    def multiplicator(self, value: MultiScore) -> None:
        for criterion, m in value:
            self[criterion] = m, self[criterion][1]
        
    @property
    def translation(self) -> MultiScore:
        return MultiScore({ criterion: value[1].to_triplet() for criterion, value in self.scales })
        
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
