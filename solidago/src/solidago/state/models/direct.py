from typing import Optional, Union, Any
from pathlib import Path
from pandas import DataFrame, Series

from .score import Score, MultiScore
from .base import ScoringModel


class DirectScoring(ScoringModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        assert self.is_base()
        
    def score(self, entity: Union[str, "Entity"]) -> MultiScore:
        return self.directs.get(entity)
        
    def to_direct(self, entities: Optional["Entities"]=None) -> "DirectScoring":
        return self

    def evaluated_entities(self, entities: "Entities") -> "Entities":
        return entities.get(set(self.directs["entity_name"]))
    
    def set(self, 
        entity: Union[str, "Entity"], 
        criterion: Optional[Union[str, MultiScore]]=None, 
        score: Optional[Union[Score, MultiScore]]=None
    ) -> None:
        if isinstance(criterion, str) and isinstance(score, Score):
            if self.user_models is None:
                self.directs.set(entity, criterion, score)
            else:
                self.user_models.directs.set(self.username, entity, criterion, score)
        else:
            assert isinstance(criterion, MultiScore) ^ isinstance(score, MultiScore)
            multiscore = score if isinstance(score, MultiScore) else criterion
            for criterion, score in multiscore:
                self.set(entity, criterion, score)
    
    def __repr__(self) -> str:
        return repr(self.directs)
