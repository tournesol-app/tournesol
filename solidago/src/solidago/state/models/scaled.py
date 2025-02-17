from typing import Union, Optional, Any
from pathlib import Path
from pandas import DataFrame

from solidago.primitives.datastructure import NestedDictOfTuples
from .score import Score, MultiScore
from .base import ScoringModel


class ScaledModel(ScoringModel):
    def __init__(self, 
        parent: ScoringModel, 
        dataframes: Optional[dict[str, DataFrame]]=None, 
        depth: int=0, 
        note: str="None",
        multipliers: Optional[MultiScore]=None,
        translations: Optional[MultiScore]=None,
        *args, 
        **kwargs
    ):
        super().__init__(parent=parent, *args, **kwargs)
        if "multipliers" not in self.dfs:
            self.dfs["multipliers"] = MultiScore(key_names=["depth", "criterion"])
        if "translations" not in self.dfs:
            self.dfs["translations"] = MultiScore(key_names=["depth", "criterion"])
    
    @property
    def multiplier(self) -> MultiScore:
        return self.dfs["multipliers"].get(depth=self.depth)
    
    @property
    def translation(self) -> MultiScore:
        return self.dfs["translation"].get(depth=self.depth)
    
    def score(self, entity: "Entity") -> MultiScore:
        return self.scale(self.parent.score(entity))

    def scale(self, score: MultiScore) -> MultiScore:
        return self.multiplier * score + self.translation
    
    def rescale(self, multiplier: Score, translation: Score) -> None:
        self.multiplier *= multiplier
        self.translation = multiplier * self.translation + translation
