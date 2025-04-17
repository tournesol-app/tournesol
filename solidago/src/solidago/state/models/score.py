import math
import numbers

from typing import Optional, Union, Any, Callable, Iterable
from pandas import Series, DataFrame

from solidago.primitives.datastructure import NestedDict, MultiKeyTable


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
            assert isinstance(left_unc, numbers.Number) and isinstance(right_unc, numbers.Number)
            values = value, left_unc, right_unc
        if math.isnan(values[0]):
            self.value, self.left_unc, self.right_unc = float("nan"), float("inf"), float("inf")
        else:
            assert values[1] >= 0 and values[2] >= 0, values
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

    def __eq__(self, score: Union[int, float, "Score"]) -> bool:
        if not isinstance(score, Score):
            score = Score(score, 0, 0)
        if self.isnan():
            return score.isnan()
        return self.to_triplet() == score.to_triplet()
        
    def __neq__(self, score: Union[int, float, "Score"]) -> bool:
        return not (self == score)
    
    def __lt__(self, score: Union[int, float, "Score"]) -> bool:
        if not isinstance(score, Score):
            score = Score(score, 0, 0)
        return self.max < score.min
    
    def __gt__(self, score: Union[int, float, "Score"]) -> bool:
        if not isinstance(score, Score):
            score = Score(score, 0, 0)
        return self.min > score.max
    
    def __le__(self, score: Union[int, float, "Score"]) -> bool:
        if not isinstance(score, Score):
            score = Score(score, 0, 0)
        return self.min <= score.max
    
    def __ge__(self, score: Union[int, float, "Score"]) -> bool:
        if not isinstance(score, Score):
            score = Score(score, 0, 0)
        return self.max >= score.min
    
    def __neg__(self) -> "Score":
        return Score(- self.value, self.right_unc, self.left_unc)
    
    def __add__(self, score: Union[int, float, "Score"]) -> "Score":
        if not isinstance(score, Score):
            score = Score(score, 0, 0)
        return Score(
            self.value + score.value,
            self.left_unc + score.left_unc,
            self.right_unc + score.right_unc
        )
    
    def __sub__(self, score: Union[int, float, "Score"]) -> "Score":
        if not isinstance(score, Score):
            score = Score(score, 0, 0)
        return Score(
            self.value - score.value,
            self.left_unc + score.right_unc,
            self.right_unc + score.left_unc
        )
        
    def __mul__(self, s: Union[int, float, "Score"]) -> "Score":
        if not isinstance(s, Score):
            s = Score(s, 0, 0)
        value = self.value * s.value
        extremes = [ self.min * s.min, self.min * s.max, self.max * s.min, self.max * s.max ]
        return Score(value, value - min(extremes), max(extremes) - value)

    def __truediv__(self, s: "Score") -> "Score":
        if not isinstance(s, Score):
            s = Score(s, 0, 0)
        if 0 in s:
            return Score.nan()
        value = self.value / s.value
        extremes = [ self.min / s.min, self.min / s.max, self.max / s.min, self.max / s.max ]
        return Score(value, value - min(extremes), max(extremes) - value)

    def abs(self) -> "Score":
        if 0 in self:
            return Score(abs(self.value), 0, max(abs(self.min), self.max) - abs(self.value))
        if self.value > 0:
            return Score(self.value, self.left_unc, self.right_unc)
        return Score(abs(self.value), self.right_unc, self.left_unc)

    def isnan(self) -> bool:
        return self.value == float("nan") or (
            self.left_unc == float("inf") and self.right_unc == float("inf")
        )
    
    def __repr__(self) -> str:
        return f"{self.value} ± [- {self.left_unc}, {self.right_unc}]"

    def __contains__(self, value: float) -> bool:
        return self.min <= value and value <= self.max
    
    # The three following methods allow to treat Score like a MultiScore object to simplify code
    @property
    def keynames(self) -> tuple:
        return tuple()

    def __iter__(self) -> Iterable:
        yield tuple(), self
    
    def get(self, *args, **kwargs) -> "Score":
        assert not args and not kwargs
        return self


class MultiScore(MultiKeyTable):
    value_cls: type=Score
    
    def __init__(self, 
        keynames: list[str]=["criterion"], 
        init_data: Optional[Union[NestedDict, Any]]=None,
        parent_tuple: Optional[tuple["Comparisons", tuple, tuple]]=None,
        name: str="scores",
        *args, **kwargs
    ):
        """ We consider the possibility of multidimensional scoring.
        In the context of Tournesol, for instance, the dimensions are the criteria.
        For scientific peer reviewing, it could be the criteria may be
        {'clarity', 'correctness', 'originality', 'rating'}. """
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)
        self.name = name

    @classmethod
    def value_factory(cls):
        return Score.nan()

    @property
    def valuenames(self) -> tuple:
        return ("value", "left_unc", "right_unc")
    
    def value2tuple(self, score: Score) -> tuple:
        return score.to_triplet()
    
    def series2value(self, previous_value: Any, row: Series) -> Score:
        return Score(row)
    
    @classmethod
    def nan(cls) -> "MultiScore":
        return MultiScore()

    def set(self, *args, **kwargs) -> None:
        """ args is assumed to list keys and then value, 
        though some may be specified through kwargs """
        assert len(args) + len(kwargs) == self.depth + 1
        if "value" in kwargs:
            value = kwargs["value"]
            del kwargs["value"]
        else:
            args, value = args[:-1], args[-1]
        assert isinstance(value, type(self).value_cls)
        if value.isnan():
            return None
        kwargs = self.keys2kwargs(*args, **kwargs)
        self._main_cache()
        for keynames in self._cache:
            keys = tuple(kwargs[kn] for kn in keynames)
            self._cache[keynames][keys] = value
        if self.parent: # Required because child may have created a cache absent from parent
            kwargs = kwargs | dict(zip(self.parent_keynames, self.parent_keys))
            self.parent.set(value, **kwargs)
    
    def __eq__(self, other: "MultiScore") -> bool:
        for keys in set(self.keys()) | set(other.keys()):
            if self[keys] != other[keys]:
                return False
        return True
        
    def __neq__(self, other: "MultiScore") -> bool:
        return not (self == other)

    def __neg__(self) -> "MultiScore":
        result = MultiScore(self.keynames)
        for keys, score in self:
            result[keys] = - score
        return result
    
    def coordinate_wise_operation(self, 
        other: Union[Score, "MultiScore"], 
        score_operation: Callable
    ) -> "MultiScore":
        common_keynames = [kn for kn in self.keynames if kn in other.keynames]
        keynames = list(self.keynames) + [kn for kn in other.keynames if kn not in common_keynames]
        result = MultiScore(keynames)
        for self_full_keys, self_score in self:
            self_full_kwargs = dict(zip(self.keynames, self_full_keys))
            common_kwargs = {kn: self_full_kwargs[kn] for kn in common_keynames}
            self_keys = [key for kn, key in self_full_kwargs.items() if kn in keynames]
            for other_keys, other_score in other.get(**common_kwargs):
                score = score_operation(self_score, other_score)
                if not keynames:
                    return score
                if not score.isnan():
                    result[tuple(self_keys + list(other_keys))] = score
        return result
    
    def __add__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        return self.coordinate_wise_operation(other, Score.__add__)
        
    def __sub__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        return self.coordinate_wise_operation(other, Score.__sub__)
    
    def __mul__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        return self.coordinate_wise_operation(other, Score.__mul__)
        
    def __truediv__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        return self.coordinate_wise_operation(other, Score.__truediv__)
