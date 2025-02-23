import numbers

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
    
    def set(self, entity: Union[str, "Entity"], *args, **kwargs) -> None:
        """ Valid values include
        - self.set(entity, multiscore: MultiScore)
        - self.set(entity, criterion: str, score: Score)
        - self.set(entity, criterion: str, value: float, left_unc: float, right_unc: float)
        """
        assert len(args) + len(kwargs) > 0
        # First construct a kwargs with all args
        if len(args) == 1 and len(kwargs) == 0:
            kwargs = dict(multiscore=args[0])
        elif len(args) + len(kwargs) == 2:
            args_keys = [k for k in ["criterion", "score"] if k not in kwargs]
            kwargs = kwargs | dict(zip(args_keys, args))
        elif len(args) + len(kwargs) == 4:
            args_keys = [k for k in ["criterion", "value", "left_unc", "right_unc"] if k not in kwargs]
            kwargs = kwargs | dict(zip(args_keys, args))
        # Now handle the different kwargs cases
        if len(kwargs) == 2: # The main one - others will call this section
            assert "criterion" in kwargs and isinstance(kwargs["criterion"], str)
            assert "score" in kwargs and isinstance(kwargs["score"], Score)
            if self.user_models is None:
                self.directs.set(entity, kwargs["criterion"], kwargs["score"])
            else:
                self.user_models.directs.set(self.username, entity, kwargs["criterion"], kwargs["score"])
        elif len(args) == 1:
            assert "multiscore" in kwargs and isinstance(kwargs["multiscore"], MultiScore)
            for criterion, score in kwargs["multiscore"]:
                self.set(entity, criterion=criterion, score=score)
        elif len(kwargs) == 4:
            assert "criterion" in kwargs and isinstance(kwargs["criterion"], str)
            assert "value" in kwargs and isinstance(kwargs["value"], numbers.Number)
            assert "left_unc" in kwargs and isinstance(kwargs["left_unc"], numbers.Number)
            assert "right_unc" in kwargs and isinstance(kwargs["right_unc"], numbers.Number)
            score = Score(kwargs["value"], kwargs["left_unc"], kwargs["right_unc"])
            self.set(entity, criterion=kwargs["criterion"], score=score)
        else:
            raise ValueError(kwargs)
    
    def __repr__(self) -> str:
        return repr(self.directs)
