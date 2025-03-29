import numbers

from typing import Optional, Union, Any
from pathlib import Path
from pandas import DataFrame, Series

from .score import Score, MultiScore
from .base import BaseModel


class DirectScoring(BaseModel):
    def __init__(self, directs: Optional[MultiScore]=None, note: str="None", *args, **kwargs):
        super().__init__(note, *args, **kwargs)
        self.directs = MultiScore(["entity_name", "criterion"], name="directs") if directs is None else directs
        
    def __call__(self, 
        entities: Union["Entity", "Entities"], 
        criterion: Optional[str]=None
    ) -> MultiScore:
        """ Assigns a score to an entity, or to multiple entities.
        
        Parameters
        ----------
        entities: Union[Entity, Entities]
            
        Returns
        -------
        out: Score or MultiScore
            If entities: Entity with unidimensional scoring, the output is a Score.
            If entities: Entity with multivariate scoring, then out[criterion_name] is a Score.
            If entities: Entities with unidimensional scoring, then out[entity_name] is a Score.
            If entities: Entities with multivariate scoring, then out[entity_name] is a MultiScore.
        """
        from solidago.state.entities import Entities
        if not isinstance(entities, Entities) and criterion is not None:
            return self.score(entities, criterion)
        if not isinstance(entities, Entities):
            return self.directs[entities]
        if criterion is None:
            return self.directs
        return self.directs.get(criterion=criterion)
    
    def score(self, entity: Union[str, "Entity"], criterion: str) -> Score:
        return self.directs[entity, criterion]
    
    def criteria(self) -> set[str]:
        return self.directs.keys("criterion")

    def evaluated_entities(self, entities: "Entities", criterion: Optional[str]=None) -> "Entities":
        multiscore = self.directs if criterion is None else self.directs.get(criterion=criterion)
        return entities.get(multiscore.keys("entity_name"))
    
    def __setitem__(self, keys: tuple, value: Score) -> None:
        self.directs[keys] = value

    def __len__(self) -> int:
        return len(self.directs)
    
    def to_direct(self, entities: Optional["Entities"]=None) -> "DirectScoring":
        return self.directs

    def get_directs(self) -> MultiScore:
        return self.directs
