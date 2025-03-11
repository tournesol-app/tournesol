from typing import Union, Optional, Any, Literal
from pathlib import Path
from pandas import DataFrame

from .score import Score, MultiScore
from .base import ScoringModel


class ScaledModel(ScoringModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert not self.is_base()
        
    @property
    def multiplier(self) -> MultiScore:
        return MultiScore(
            data=self.scales.get(depth=str(self.depth), kind="multiplier"),
            default_value=Score(1, 0, 0)
        )
    
    @property
    def translation(self) -> MultiScore:
        return MultiScore(
            self.scales.get(depth=self.depth, kind="translation"),
            default_value=Score(0, 0, 0)
        )
    
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
    
    def score(self, entity: "Entity", criterion: str) -> Score:
        return self.scale(self.parent.score(entity, criterion), criterion)

    def scale(self, score: Score, criterion: str) -> Score:
        return self.multiplier.get(criterion) * score + self.translation.get(criterion)
    
    def rescale(self, multiplier: Score, translation: Score) -> None:
        self.multiplier *= multiplier
        self.translation = multiplier * self.translation + translation
