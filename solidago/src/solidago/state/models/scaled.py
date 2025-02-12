from typing import Union, Optional, Any
from pathlib import Path
from pandas import DataFrame

from solidago.primitives.datastructure import NestedDictOfTuples
from .score import Score, MultiScore
from .base import ScoringModel


class ScaledModel(ScoringModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.multiplicators = self.dfs["multiplicators"][str(self.depth)]
        self.translations = self.dfs["translations"][str(self.depth)]
    
    def score(self, entity: "Entity") -> MultiScore:
        return self.scale(self.parent.score(entity))

    def scale(self, score: MultiScore) -> MultiScore:
        return self.multiplicator * score + self.translation
    
    def rescale(self, multiplicator: Score, translation: Score) -> None:
        self.multiplicator *= multiplicator
        self.translation = multiplicator * self.translation + translation
