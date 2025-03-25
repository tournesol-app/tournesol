from typing import Union, Callable, Optional, Any, Literal
from pathlib import Path
from pandas import DataFrame

from .score import Score, MultiScore
from .base import ScoringModel, DerivedModel


class Multiplier(MultiScore):
    name: str="multipliers"
    value_factory: Callable=Score(1, 0, 0)
    
    def __init__(self, 
        keynames: list[str]=["criterion"], 
        init_data: Optional[Union[Any]]=None,
        parent_tuple: Optional[tuple["Comparisons", tuple, tuple]]=None,
        *args, **kwargs
    ):
        """ We consider the possibility of multidimensional scoring.
        In the context of Tournesol, for instance, the dimensions are the criteria.
        For scientific peer reviewing, it could be the criteria may be
        {'clarity', 'correctness', 'originality', 'rating'}. """
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)
        
        
class Translation(MultiScore):
    name: str="translations"
    value_factory: Callable=Score(0, 0, 0)
    
    def __init__(self, 
        keynames: list[str]=["criterion"], 
        init_data: Optional[Union[Any]]=None,
        parent_tuple: Optional[tuple["Comparisons", tuple, tuple]]=None,
        *args, **kwargs
    ):
        """ We consider the possibility of multidimensional scoring.
        In the context of Tournesol, for instance, the dimensions are the criteria.
        For scientific peer reviewing, it could be the criteria may be
        {'clarity', 'correctness', 'originality', 'rating'}. """
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)


class ScaledModel(DerivedModel):
    def __init__(self, 
        parent: Union[ScoringModel, list, tuple], 
        scales: Optional[MultiScore]=None, 
        note: str="None", 
        *args, **kwargs
    ):
        super().__init__(parent, note, *args, **kwargs)
        self.scales = scales or MultiScore(["height", "kind", "criterion"])
        self._multiplier, self._translation = None, None
    
    def get_scales(self) -> MultiScore:
        return self.scales
    
    @property
    def multiplier(self) -> Multiplier:
        if self._multiplier is None:
            keynames = [kn for kn in self.scales.keynames if kn not in ["height", "kind"]]
            self._multiplier = Multiplier(keynames, self.scales[self.height, "multiplier"])
        return self._multiplier
    
    @property
    def translation(self) -> Translation:
        if self._translation is None:
            keynames = [kn for kn in self.scales.keynames if kn not in ["height", "kind"]]
            return Translation(keynames, self.scales[self.height, "translation"])
        return self._translation

    def set_multiplier(self, criterion: str, multiplier: Score) -> None:
        self.scales[self.height, "multiplier", criterion] = multiplier
        
    def set_translation(self, criterion: str, translation: Score) -> None:
        self.scales[self.height, "translation", criterion] = translation

    def __setitem__(self, keys: tuple, value: Score) -> None:
        if len(keys) == 2:
            keys = tuple([self.height] + list(keys))
        assert isinstance(keys[0], int) 
        assert keys[1] in {"multiplier", "translation"} 
        assert isinstance(keys[2], str)
        self.scales[keys] = value
        
    def score(self, entity: "Entity", criterion: str) -> Score:
        return self.scale(self.parent.score(entity, criterion), criterion)

    def scale(self, score: Score, criterion: str) -> Score:
        return self.multiplier[criterion] * score + self.translation[criterion]
    
    def rescale(self, multiplier: Score, translation: Score) -> None:
        self.multiplier *= multiplier
        self.translation = multiplier * self.translation + translation
