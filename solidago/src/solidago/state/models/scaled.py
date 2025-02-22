from typing import Union, Optional, Any, Literal
from pathlib import Path
from pandas import DataFrame

from solidago.primitives.datastructure import NestedDictOfTuples
from .score import Score, MultiScore
from .base import ScoringModel


class ScaledModel(ScoringModel):
    def __init__(self, 
        parent: ScoringModel, 
        scales: Optional[Union[str, DataFrame, MultiScore]]=None,
        depth: int=0, 
        note: str="None",
        username: Optional[str]=None,
        user_models: Optional["UserModels"]=None,
        **kwargs
    ):
        super().__init__(parent, depth, note, username, user_models, scales=scales, **kwargs)
        self.scales = MultiScore.load(directs, key_names=["depth", "kind", "criterion"])
    
    @property
    def multiplier(self) -> MultiScore:
        return self.scales.get(depth=self.depth, kind="multiplier")
    
    @property
    def translation(self) -> MultiScore:
        return self.scales.get(depth=self.depth, kind="translation")
    
    def set(self, 
        kind: Literal["multiplier", "translation"], 
        criterion: Optional[Union[str, MultiScore]]=None, 
        score: Optional[Union[Score, MultiScore]]=None
    ) -> None:
        if isinstance(criterion, str) and isinstance(score, Score):
            if self.user_models is None:
                self.directs.set(self.depth, kind, criterion, score)
            else:
                self.user_models.scales.set(self.username, self.depth, kind, criterion, score)
        else:
            assert isinstance(criterion, MultiScore) ^ isinstance(score, MultiScore)
            multiscore = score if isinstance(score, MultiScore) else criterion
            for criterion, score in multiscore:
                self.set(kind, criterion, score)
    
    def set_multiplier(self, 
        criterion: Optional[Union[str, MultiScore]]=None, 
        score: Optional[Union[Score, MultiScore]]=None
    ) -> None:
        self.set("multiplier", criterion, score)
    
    def set_translation(self, 
        criterion: Optional[Union[str, MultiScore]]=None, 
        score: Optional[Union[Score, MultiScore]]=None
    ) -> None:
        self.set("translation", criterion, score)
    
    def score(self, entity: "Entity") -> MultiScore:
        return self.scale(self.parent.score(entity))

    def scale(self, score: MultiScore) -> MultiScore:
        return self.multiplier * score + self.translation
    
    def rescale(self, multiplier: Score, translation: Score) -> None:
        self.multiplier *= multiplier
        self.translation = multiplier * self.translation + translation
