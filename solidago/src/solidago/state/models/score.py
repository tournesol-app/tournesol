from typing import Optional, Union
from pandas import DataFrame, Series

from solidago.primitives.datastructure.nested_dict import NestedDict


class Score:
    def __init__(self, 
        value: Union[float, list, tuple, dict, Series, "Score"], 
        left_unc: Optional[float]=None, 
        right_unc: Optional[float]=None
    ):
        """ In collaborative scaling, it is important to account for varying degrees of reliability,
        not only between different users' judgments, but even more so between the preference models
        learned for the users given their provided data.
        
        Here, we consider scoring models based on potentially asymmetric score uncertainties.
        Note that more sophisticated models of uncertainties may be considered in the future,
        such as score difference uncertainties, or high-dimensional uncertainties. 
        
        The class Score not only describes the asymmetric left and right uncertainties,
        but also some basic algebra between such scores with asymmetric uncertainties. """
        if isinstance(value, Score):
            assert left_unc is None and right_unc is None
            values = value.value, value.left_unc, value.right_unc
        elif isinstance(value, (dict, Series)):
            assert left_unc is None and right_unc is None
            values = value["value"], value["left_unc"], value["right_unc"]
        elif isinstance(value, (list, tuple)):
            assert left_unc is None and right_unc is None
            values = value
        else:
            assert isinstance(left_unc, float) and isinstance(right_unc, float)
            values = value, left_unc, right_unc
        assert values[1] >= 0 and values[2] >= 0
        self.value, self.left_unc, self.right_unc = values
    
    @classmethod
    def nan(cls):
        return cls(float("nan"), float("inf"), float("inf"))
    
    @property
    def score(self) -> float:
        return self.value

    @property
    def min(self) -> float:
        return self.value - self.left_unc
    
    @property
    def max(self) -> float:
        return self.value + self.right_unc
    
    def to_triplet(self) -> tuple[float, float, float]:
        return self.value, self.left_unc, self.right_unc
    
    def to_dict(self) -> dict[str, float]:
        return dict(value=self.value, left_unc=self.left_unc, right_unc=self.right_unc)
    
    def average_uncertainty(self) -> float:
        return (self.left_unc + self.right_unc) / 2
    
    def __neg__(self) -> "Score":
        return Score(- self.value, self.right_unc, self.left_unc)
    
    def __add__(self, score: "Score") -> "Score":
        return Score(
            self.value + score.value,
            self.left_unc + score.left_unc,
            self.right_unc + score.right_unc
        )
    
    def __mul__(self, s: "Score") -> "Score":
        extremes = [ self.min * s.min, self.min * s.max, self.max * s.min, self.max * s.max ]
        value = self.value * s.value
        return Score(value, value - min(extremes), max(extremes) - value)

    def isnan(self) -> bool:
        return self.value == float("nan") or (
            self.left_unc == float("inf") and self.right_unc == float("inf")
        )
    
    def __repr__(self) -> str:
        return f"{self.value} ± [- {self.left_unc}, {self.right_unc}]"


class MultiScore(NestedDict):
    def __init__(self, 
        d: Optional[Union[NestedDict, dict, DataFrame]]=None,
        key_names: list[str]=["criterion"], 
        value_names: list[str]=["score", "left_unc", "right_unc"],
        save_filename: Optional[str]=None,
    ):
        """ We consider the possibility of multidimensional scoring.
        In the context of Tournesol, for instance, the dimensions are the criteria.
        For scientific peer reviewing, it could be the criteria may be
        {'clarity', 'correctness', 'originality', 'rating'}. """
        super().__init__(d=d, key_names=key_names, value_names=value_names, save_filename=None)

    def default_value(self) -> Score:
        return Score.nan()
    
    def process_stored_value(self, keys: list[str], stored_value: tuple[float, float, float]) -> Score:
        return Score(*stored_value)
    
    @classmethod
    def nan(cls) -> "MultiScore":
        return MultiScore()

    def __neg__(self) -> "MultiScore":
        return MultiScore({ key: - value for key, value in self })
    
    def __add__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        if isinstance(other, Score):
            return MultiScore({ key: value + other for key, value in self })
        keys = self.get_set("criterion") & other.get_set("criterion")
        return MultiScore({ key: self[key] + other[key] for key in keys })
    
    def __mul__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        if isinstance(other, Score):
            return MultiScore({ key: value * other for key, value in self })
        keys = self.get_set("criterion") & other.get_set("criterion")
        return MultiScore({ key: self[key] * other[key] for key in keys })
