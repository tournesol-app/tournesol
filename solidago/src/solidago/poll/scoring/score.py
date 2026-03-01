from copy import deepcopy

import itertools
from typing import Any, Callable, Hashable, Iterable, Iterator, Self, Union
from pandas import Series

from solidago.primitives.datastructure import Row, FilteredTable
from solidago.poll.poll_tables import *


class Score(Row):
    default: dict[str, Any] = dict(value=np.nan, left_unc=0., right_unc=0.)

    def __init__(self, 
        arg: Union[float, list, tuple, dict, Series, "Score"] | None = None, 
        series: pd.Series | None = None, 
        *args: Any, **kwargs: Any
    ):
        """ In collaborative scaling, it is important to account for varying degrees of reliability,
        not only between different users' judgments, but even more so between the preference models
        learned for the users given their provided data.
        
        Here, we consider scoring models based on potentially asymmetric score uncertainties.
        Note that more sophisticated models of uncertainties may be considered in the future,
        such as score difference uncertainties, or high-dimensional uncertainties. 
        
        The class Score not only describes the asymmetric left and right uncertainties,
        but also some basic algebra between such scores with asymmetric uncertainties. """
        if arg is None:
            super().__init__(series, *args, **kwargs)
        elif isinstance(arg, Score):
            super().__init__(series, *args, value=arg.value, left_unc=arg.left_unc, right_unc=arg.right_unc, **kwargs)
        elif isinstance(arg, (dict, Series)):
            super().__init__(series, *args, **dict(arg), **kwargs)
        elif isinstance(arg, (list, tuple)):
            assert len(arg) == 3, arg
            value, left_unc, right_unc = arg
            super().__init__(series, *args, value=value, left_unc=left_unc, right_unc=right_unc, **kwargs)
        else:
            super().__init__(series, *args, value=float(arg), **kwargs)
    
    @classmethod
    def nan(cls) -> Self:
        return cls((np.nan, np.inf, np.inf))
    
    @property
    def value(self) -> float:
        return self.series["value"] # type: ignore
    
    @property
    def left_unc(self) -> float:
        return self.series["left_unc"] # type: ignore
    
    @property
    def right_unc(self) -> float:
        return self.series["right_unc"] # type: ignore

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

    def __eq__(self, score: object) -> bool:
        if not isinstance(score, Score):
            try:
                score = Score(float(score)) # type: ignore - error caught
            except:
                raise ValueError(f"Cannot make {score} (type {type(score).__name__}) a float")
        if self.isnan():
            return score.isnan()
        return self.to_triplet() == score.to_triplet()
        
    def __neq__(self, score: Union[int, float, "Score"]) -> bool:
        return not (self == score)
    
    def __lt__(self, score: Union[int, float, "Score"]) -> bool:
        """ Holds if any value of self is less than any value of score """
        if not isinstance(score, Score):
            score = Score(score)
        return self.max < score.min
    
    def __gt__(self, score: Union[int, float, "Score"]) -> bool:
        """ Holds if any value of self is more than any value of score """
        if not isinstance(score, Score):
            score = Score(score)
        return self.min > score.max
    
    def __le__(self, score: Union[int, float, "Score"]) -> bool:
        """ Holds if some value of self is less than some value of score """
        if not isinstance(score, Score):
            score = Score(score)
        return self.min <= score.max
    
    def __ge__(self, score: Union[int, float, "Score"]) -> bool:
        """ Holds if some value of self is more than some value of score """
        if not isinstance(score, Score):
            score = Score(score)
        return self.max >= score.min
    
    def set_score(self, value: float | None = None, left_unc: float | None = None, right_unc: float | None = None):
        if value is not None:
            self["value"] = value
        if left_unc is not None:
            self["left_unc"] = left_unc
        if right_unc is not None:
            self["right_unc"] = right_unc

    def __neg__(self) -> "Score":
        result = deepcopy(self)
        result.set_score(-self.value, self.right_unc, self.left_unc)
        return result
    
    def __add__(self, score: Union[int, float, "Score", "Scores"]) -> Union["Score", "Scores"]:
        if isinstance(score, Scores):
            return score + self
        score = score if isinstance(score, Score) else Score(score)
        result = deepcopy(self)
        result.set_score(self.value + score.value, self.left_unc + score.left_unc, self.right_unc + score.right_unc)
        return result
    
    def __sub__(self, score: Union[int, float, "Score", "Scores"]) -> Union["Score", "Scores"]:
        if isinstance(score, Scores):
            return score * self
        score = score if isinstance(score, Score) else Score(score)
        result = deepcopy(self)
        result.set_score(self.value - score.value, self.left_unc + score.right_unc, self.right_unc + score.left_unc)
        return result
        
    def __mul__(self, s: Union[int, float, "Score", "Scores"]) -> Union["Score", "Scores"]:
        if isinstance(s, Scores):
            return s * self
        s = s if isinstance(s, Score) else Score(s)
        value = self.value * s.value
        extremes = [ self.min * s.min, self.min * s.max, self.max * s.min, self.max * s.max ]
        result = deepcopy(self)
        result.set_score(value, value - min(extremes), max(extremes) - value)
        return result

    def __truediv__(self, s: Union[int, float, "Score"]) -> "Score":
        s = s if isinstance(s, Score) else Score(s)
        result = deepcopy(self)
        if s.contains(0):
            result.set_score(np.nan)
            return result
        value = self.value / s.value
        extremes = [ self.min / s.min, self.min / s.max, self.max / s.min, self.max / s.max ]
        result.set_score(value, value - min(extremes), max(extremes) - value)
        return result

    def abs(self) -> "Score":
        result = deepcopy(self)
        if self.contains(0):
            result.set_score(abs(self.value), abs(self.value), max(abs(self.min), self.max) - abs(self.value))
        elif self.value > 0:
            result.set_score(self.value, self.left_unc, self.right_unc)
        else:
            result.set_score(abs(self.value), self.right_unc, self.left_unc)
        return result

    def isnan(self) -> bool:
        return np.isnan(self.value) or (
            self.left_unc == float("inf") and self.right_unc == float("inf")
        )
    
    def __repr__(self) -> str:
        return f"{self.value} ± [- {self.left_unc}, {self.right_unc}]"

    def contains(self, value: float) -> bool:
        return self.min <= value and value <= self.max
    
    # The following methods allow to treat Score like a MultiScore object to simplify code
    def __iter__(self) -> Iterator["Score"]:
        yield self
    
    def get(self, *keys: Hashable) -> "Score":
        assert not keys
        return self


class Scores(FilteredTable[Score]):
    TableRowType: type = Score
    name: str = "scores"
    default_column_names: list[str] = ["value", "left_unc", "right_unc"]
    default_dtypes: dict[str, DTypeLike] = dict(value=np.float64, left_unc=np.int64, right_unc=np.int64)
    default_default_score: tuple[float, float, float] = np.nan, np.inf, np.inf

    def __init__(self, 
        *args, 
        default_score: tuple[float, float, float] | None = None, 
        default_score_factory: Callable[..., Score] | None = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.default_score = default_score or self.default_default_score
        self._default_score_factory = default_score_factory
    
    def filters_kwargs(self) -> dict[str, Any]:
        return dict(default_score=self.default_score, default_score_factory=self._default_score_factory)

    def row_factory(self, **keys: Hashable) -> Score:
        if self._default_score_factory is not None:
            return self._default_score_factory(**keys)
        return self.TableRowType(None, **(keys | dict(zip(["value", "left_unc", "right_unc"], self.default_score))))
    
    @property
    def value(self) -> NDArray[np.float64]:
        return self.get_column("value").to_numpy(np.float64)
    
    @property
    def left_unc(self) -> NDArray[np.float64]:
        return self.get_column("left_unc").to_numpy(np.float64) # type: ignore
    
    @property
    def right_unc(self) -> NDArray[np.float64]:
        return self.get_column("right_unc").to_numpy(np.float64) # type: ignore
    
    @property
    def min(self) -> NDArray[np.float64]:
        return self.value - self.left_unc
    
    @property
    def max(self) -> NDArray[np.float64]:
        return self.value + self.right_unc

    def __eq__(self, other: object) -> bool:
        assert isinstance(other, Scores), (other, type(other))
        assert self.keynames == other.keynames, (self.keynames, other.keynames)
        for row in self:
            keys = {keyname: row[keyname] for keyname in self.keynames}
            assert row == other.get("unique", **keys)
        for row in other:
            keys = {keyname: row[keyname] for keyname in self.keynames}
            assert row == self.get("unique", **keys)
        return True
        
    def __neq__(self, other: "Scores") -> bool:
        return not (self == other)

    def __neg__(self) -> "Scores":
        result = deepcopy(self)
        result.set_columns(value=self.value, left_unc=self.left_unc, right_unc=self.right_unc)
        return result
    
    def cw_operation(self, other: Union[Score, "Scores"], op: Callable[[Score, Score], Union[Score, "Scores"]]) -> Union[Score, "Scores"]:
        
        def default_score_factory(**keys) -> Score:
            score = self.get(**{name: key for name, key in keys.items() if name in self.keynames})
            if isinstance(other, Score):
                score = op(score, other)
            else:
                assert isinstance(other, Scores)
                score = op(score, other.get(**{name: key for name, key in keys.items() if name in other.keynames}))
            assert isinstance(score, Score)
            return score
            
        if isinstance(other, Score):
            others = Scores(keynames=[])
            others.set(other)
            return self.cw_operation(others, op)
        
        common_keynames = list(self.keynames & other.keynames)
        result_keynames = self.keynames | other.keynames
        result = Scores(keynames=result_keynames, default_score_factory=default_score_factory)
        keys_tuples = {tuple(s[name] for name in common_keynames) for s in itertools.chain(self, other)}
        for keys_tuple in keys_tuples:
            common_keys = dict(zip(common_keynames, keys_tuple))
            filtered_self, filtered_other = self.filters(**common_keys), other.filters(**common_keys)
            for self_score, other_score in itertools.product(filtered_self, filtered_other):
                keys = common_keys | {n: self_score[n]for n in self.keynames - set(common_keynames)} | \
                    {n: other_score[n]for n in other.keynames - set(common_keynames)}
                score = op(self_score, other_score)
                if isinstance(score, Score):
                    result.set(score, **keys)
            if other.keynames.issubset(common_keynames) and not filtered_other:
                for self_score in filtered_self:
                    score = op(self_score, other.get(**common_keys))
                    if isinstance(score, Score):
                        result.set(score, **common_keys)
            if self.keynames.issubset(common_keynames) and not filtered_self:
                for other_score in filtered_other:
                    score = op(other_score, self.get(**common_keys))
                    if isinstance(score, Score):
                        result.set(score, **common_keys)
        
        return result
    
    def __add__(self, other: Union[Score, "Scores"]) -> Union[Score, "Scores"]:
        if isinstance(other, Score):
            result = deepcopy(self)
            result.set_columns(
                value=self.value + other.value,
                left_unc=self.left_unc + other.left_unc,
                right_unc=self.right_unc + other.right_unc
            )
            def default_score_factory(**keys) -> Score:
                score = self.get(**{name: key for name, key in keys.items() if name in self.keynames}) + other
                assert isinstance(score, Score)
                return score
            result._default_score_factory = default_score_factory
            return result
        return self.cw_operation(other, Score.__add__)
        
    def __sub__(self, other: Union[Score, "Scores"]) -> Union[Score, "Scores"]:
        return self + (- other)
    
    def __mul__(self, other: Union[Score, "Scores"]) -> Union[Score, "Scores"]:
        if isinstance(other, Score):
            result = deepcopy(self)
            extremes = np.stack([self.min * other.min, self.min * other.max, self.max * other.min, self.max * other.max])
            value = result.value * other.value
            left_unc = value - np.min(extremes, axis=1)
            right_unc = np.max(extremes, axis=1) - value
            result.set_columns(value=value, left_unc=left_unc, right_unc=right_unc)
            def default_score_factory(**keys) -> Score:
                score = self.get(**{name: key for name, key in keys.items() if name in self.keynames}) * other
                assert isinstance(score, Score)
                return score
            result._default_score_factory = default_score_factory
            return result
        return self.cw_operation(other, Score.__mul__)
        
    def __truediv__(self, other: Union[Score, "Scores"]) -> Union[Score, "Scores"]:
        if isinstance(other, Score):
            result = deepcopy(self)
            extremes = np.stack([self.min * other.min, self.min * other.max, self.max * other.min, self.max * other.max])
            value = result.value * other.value
            left_unc = value - np.min(extremes, axis=1)
            right_unc = np.max(extremes, axis=1) - value
            result.set_columns(value=value, left_unc=left_unc, right_unc=right_unc)
            def default_score_factory(**keys) -> Score:
                score = self.get(**{name: key for name, key in keys.items() if name in self.keynames}) / other
                assert isinstance(score, Score)
                return score
            result._default_score_factory = default_score_factory
            return result
        return self.cw_operation(other, Score.__truediv__)

    def abs(self) -> "Scores":
        value, min, max = self.value, self.min, self.max
        abs_value = np.abs(value)
        left_unc = np.where(min * max < 0, abs_value, np.where(value > 0, self.left_unc, self.right_unc))
        right_unc = np.where(
            min * max < 0, 
            np.max([np.abs(min), max]) - abs_value, 
            np.where(value > 0, self.right_unc, self.left_unc)
        )
        result = deepcopy(self)
        result.set_columns(value=value, left_unc=left_unc, right_unc=right_unc)
        return result
