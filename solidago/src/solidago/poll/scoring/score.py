from copy import deepcopy
from typing import Any, Callable, Hashable, Iterator, Self, Union, overload
from pandas import Series
from numba import njit

import itertools

from solidago.primitives.datastructure import Row, FilteredTable
from solidago.poll.poll_tables import *
from solidago.primitives.datastructure.filtered_table import SelectUnique


class Score(Row):
    default_default_values: dict[str, Any] = dict(value=np.nan, left_unc=0., right_unc=0.)

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
        return float(self.series["value"])
    
    @property
    def left_unc(self) -> float:
        return float(self.series.get("left_unc", 0))
    
    @property
    def right_unc(self) -> float:
        return float(self.series.get("right_unc", 0))

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
        
    def __neq__(self, score: int | float | np.number | Self) -> bool:
        return not (self == score)
    
    def __lt__(self, score: int | float | np.number | Self) -> bool:
        """ Holds if any value of self is less than any value of score """
        return self.max < (score.min if isinstance(score, Score) else float(score))
    
    def __gt__(self, score: Union[int, float, "Score"]) -> bool:
        """ Holds if any value of self is more than any value of score """
        return self.min > (score.max if isinstance(score, Score) else float(score))
    
    def __le__(self, score: Union[int, float, "Score"]) -> bool:
        """ Holds if some value of self is less than some value of score """
        return self.min <= (score.max if isinstance(score, Score) else float(score))
    
    def __ge__(self, score: Union[int, float, "Score"]) -> bool:
        """ Holds if some value of self is more than some value of score """
        return self.max >= (score.min if isinstance(score, Score) else float(score))
    
    def set_score(self, 
        value: int | float | np.number | None = None, 
        left_unc: int | float | np.number | None = None, 
        right_unc: int | float | np.number | None = None
    ):
        if value is not None:
            self["value"] = float(value)
        if left_unc is not None:
            self["left_unc"] = float(left_unc)
        if right_unc is not None:
            self["right_unc"] = float(right_unc)

    def __neg__(self) -> Self:
        result = deepcopy(self)
        result.set_score(-self.value)
        if "right_unc" in self:
            result.set_score(left_unc=self.right_unc)
        if "left_unc" in self:
            result.set_score(right_unc=self.left_unc)
        return result
    
    @overload
    def __add__(self, score: int | float | np.number | Self) -> Self: ...
    @overload
    def __add__(self, score: "Scores") -> "Scores": ...
    def __add__(self, score):
        if isinstance(score, Scores):
            return score + self
        score_value = score.value if isinstance(score, Score) else float(score)
        result = deepcopy(self)
        result.set_score(self.value + score_value)
        if "left_unc" in self or (isinstance(score, Score) and "left_unc" in score):
            result.set_score(left_unc=self.left_unc + score.left_unc)
        if "right_unc" in self or (isinstance(score, Score) and "right_unc" in score):
            result.set_score(right_unc=self.right_unc + score.right_unc)
        return result
    
    @overload
    def __sub__(self, score: int | float | np.number | Self) -> Self: ...
    @overload
    def __sub__(self, score: "Scores") -> "Scores": ...
    def __sub__(self, score):
        if isinstance(score, Scores):
            return score * self
        score_value = score.value if isinstance(score, Score) else float(score)
        result = deepcopy(self)
        result.set_score(self.value - score_value)
        if "left_unc" in self or (isinstance(score, Score) and "right_unc" in score):
            result.set_score(left_unc=self.left_unc + score.right_unc)
        if "right_unc" in self or (isinstance(score, Score) and "left_unc" in score):
            result.set_score(right_unc=self.right_unc + score.left_unc)
        return result
        
    @overload
    def __mul__(self, score: int | float | np.number | Self) -> Self: ...
    @overload
    def __mul__(self, score: "Scores") -> "Scores": ...
    def __mul__(self, score):
        if isinstance(score, Scores):
            return score * self
        result = deepcopy(self)
        if isinstance(score, (int, float, np.number)):
            value = float(score)
            result.set_score(value=self.value * value)
            if "left_unc" in self:
                if value >= 0:
                    result.set_score(left_unc=self.left_unc*value)
                else:
                    result.set_score(right_unc=-self.left_unc*value)
            if "right_unc" in self:
                if value >= 0:
                    result.set_score(right_unc=self.right_unc*value)
                else:
                    result.set_score(left_unc=-self.right_unc*value)            
            return result
        if "left_unc" not in self and "right_unc" not in self:
            return score * self
        assert isinstance(score, Score)
        value = self.value * score.value
        extremes = [
            self.min * score.min, self.min * score.max, 
            self.max * score.min, self.max * score.max 
        ]
        result.set_score(value, value - min(extremes), max(extremes) - value)
        return result
        
    def __truediv__(self, score: int | float | np.number | Self) -> Self:
        if isinstance(score, (int, float, np.number)):
            if score == 0.:
                result = deepcopy(self)
                result.set_score(np.nan)
                return result
            return self * (1./score)
        result = deepcopy(self)
        if score.contains(0):
            result.set_score(np.nan)
            return result
        value = self.value / score.value
        extremes = [ self.min / score.min, self.min / score.max, self.max / score.min, self.max / score.max ]
        result.set_score(value, value - min(extremes), max(extremes) - value)
        return result

    def abs(self) -> Self:
        result = deepcopy(self)
        if "left_unc" not in self and "right_unc" not in self:
            result.set_score(abs(self.value))
        elif self.contains(0):
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
    # def __iter__(self) -> Iterator[Self]:
    #     yield self
    

class Scores(FilteredTable[Score]):
    TableRowType: type = Score
    name: str = "scores"
    default_column_names: list[str] = ["value", "left_unc", "right_unc"]
    default_dtypes: dict[str, DTypeLike] = dict(value=np.float64, left_unc=np.int64, right_unc=np.int64)
    default_default_score: Score = Score.nan()

    def __init__(self, 
        *args, 
        default_score: Score | Callable[..., Score] | None = None,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        if default_score is None:
            self.default_score = self.default_default_score
            self._default_score_factory = None
        elif isinstance(default_score, Score):
            self.default_score = default_score
            self._default_score_factory = None
        else:
            self.default_score = self.default_default_score
            self._default_score_factory = default_score
    
    def filters_kwargs(self) -> dict[str, Any]:
        return dict(default_score=self.default_score, default_score_factory=self._default_score_factory)

    def row_factory(self, **keys: Hashable) -> Score:
        if self._default_score_factory is not None:
            return self._default_score_factory(**keys)
        return self.TableRowType(None, **keys | self.default_score.to_dict())
    
    @property
    def value(self) -> NDArray[np.float64]:
        return self("value", np.nan).astype(np.float64)
    
    @property
    def left_unc(self) -> NDArray[np.float64]:
        return np.nan_to_num(self("left_unc", 0.).astype(np.float64))
    
    @property
    def right_unc(self) -> NDArray[np.float64]:
        return np.nan_to_num(self("right_unc", 0.).astype(np.float64))
    
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
            assert row == other.get(SelectUnique(), **keys)
        for row in other:
            keys = {keyname: row[keyname] for keyname in self.keynames}
            assert row == self.get(SelectUnique(), **keys)
        return True
        
    def __neq__(self, other: Self) -> bool:
        return not (self == other)

    def __neg__(self) -> Self:
        result = deepcopy(self)
        result.set_columns(value=self.value)
        if "left_unc" in self.columns:
            result.set_columns(left_unc=self.left_unc)
        if "right_unc" in self.columns:
            result.set_columns(right_unc=self.right_unc)
        return result
    
    def _result_keys(self, other: Union[int, float, np.number, Score, Self]) -> tuple[
        dict[str, list] | dict[str, NDArray], # keys
        tuple[NDArray, NDArray | None, NDArray | None], # self (value, left_unc, right_unc)
        tuple[NDArray | float, NDArray | float | None, NDArray | float | None], # other
    ]:
        
        if isinstance(other, (int, float, np.number, Score)):
            keys = {kn: self(kn) for kn in self.keynames}
            self_left_unc = self.left_unc if "left_unc" in self.columns else None
            self_right_unc = self.right_unc if "right_unc" in self.columns else None
            self_tuple = self.value, self_left_unc, self_right_unc
            if isinstance(other, Score):
                return keys, self_tuple, other.to_triplet()
            return keys, self_tuple, (float(other), None, None)
        
        self_keys = tuple(self(keyname, filtered=False) for keyname in self.keynames)
        other_keys = tuple(other(keyname, filtered=False) for keyname in other.keynames)

        keys, common_keys_list, self_indices, other_indices = _Njit.indices(
            self.keynames, other.keynames, self_keys, other_keys,
            self.indices.astype(np.int64), other.indices.astype(np.int64), 
            self.keys_indices(), other.keys_indices(),
        )
        assert len(self_indices) == len(other_indices)
        if len(self_indices) == 0:
            e = np.array([], dtype=np.float64)
            return keys, (e, e, e), (e, e, e)

        self_scores = self._extract_from_indices(common_keys_list, self_indices)
        other_scores = other._extract_from_indices(common_keys_list, other_indices)
        return keys, self_scores, other_scores
    
    def _extract_from_indices(self, 
        keys_list: list[dict[str, Hashable]],
        indices: NDArray[np.int64]
    ) -> tuple[NDArray[np.float64], NDArray[np.float64] | None, NDArray[np.float64] | None]:
        
        if len(indices) == 0:
            empty = np.array([], dtype=np.float64)
            return empty, empty, empty
        
        left_uncs, right_uncs = None, None
        if len(self) == 0:
            if self._default_score_factory is None:
                n, (v, l, r) = len(indices), self.default_score.to_triplet()
                return np.full(n, v), np.full(n, l), np.full(n, r)
            scores = [self._default_score_factory(**keys_list[i]) for i in indices]
            return (
                np.array([s.value for s in scores]),
                np.array([s.left_unc for s in scores]),
                np.array([s.right_unc for s in scores]),
            )
        
        values = self("value", filtered=False)[indices].astype(np.float64)
        if "left_unc" in self.columns:
            left_uncs = self("left_unc", filtered=False)[indices].astype(np.float64)
        if "right_unc" in self.columns:
            right_uncs = self("right_unc", filtered=False)[indices].astype(np.float64)

        default_indices = np.where(indices == -1)[0]
        if len(default_indices) == 0:
            return values, left_uncs, right_uncs

        if self._default_score_factory is None:
            values[default_indices] = self.default_score.value
            if left_uncs is not None:
                left_uncs[default_indices] = self.default_score.left_unc
            if right_uncs is not None:
                right_uncs[default_indices] = self.default_score.right_unc
        else:
            for i in default_indices:
                score = self._default_score_factory(**keys_list[i])
                values[i] = score.value
                if left_uncs is not None:
                    left_uncs[i] = score.left_unc
                if right_uncs is not None:
                    right_uncs[i] = score.right_unc
        
        return values, left_uncs, right_uncs

    def _result_default_score(self, 
        other: Union[int, float, np.number, Score, Self], 
        op: Callable[[Score, int | float | np.number | Score], Score],
    ) -> Score | Callable[..., Score]:
        
        if self._default_score_factory is None:
            if isinstance(other, (int, float, np.number, Score)):
                return op(self.default_score, other)
            if other._default_score_factory is None:
                return op(self.default_score, other.default_score)
        
        def f(**keys) -> Score:
            score = self.get(**{n: k for n, k in keys.items() if n in self.keynames})
            if isinstance(other, (int, float, np.number, Score)):
                return op(score, other)
            subkeys = {n: k for n, k in keys.items() if n in other.keynames}
            return op(score, other.get(**subkeys))
        
        return f
    
    def __add__(self, other: Union[Score, Self]) -> Self:
        keys, (v1, l1, r1), (v2, l2, r2) = self._result_keys(other)
        keynames = list(keys.keys())
        left_uncs, right_uncs = None, None

        result = type(self)(keys, 
            keynames=keynames, columns=keynames,
            default_score=self._result_default_score(other, Score.__add__)
        )
        result.set_columns(value=v1+v2)

        if l1 is not None or l2 is not None:
            left_uncs = l2 if l1 is None else (l1 if l2 is None else l1+l2)
            result.set_columns(left_unc=left_uncs)
        if r1 is not None or r2 is not None:
            right_uncs = r2 if r1 is None else (r1 if r2 is None else r1+r2)
            result.set_columns(right_unc=right_uncs)

        return result
    
    def __sub__(self, other: Union[Score, Self]) -> Self:
        keys, (v1, l1, r1), (v2, l2, r2) = self._result_keys(other)
        keynames = list(keys.keys())
        left_uncs, right_uncs = None, None

        result = type(self)(keys, 
            keynames=keynames, columns=keynames,
            default_score=self._result_default_score(other, Score.__sub__),
        )
        result.set_columns(value=v1-v2)

        if l1 is not None or r2 is not None:
            left_uncs = r2 if l1 is None else (l1 if r2 is None else l1+r2)
            result.set_columns(left_unc=left_uncs)
        if r1 is not None or l2 is not None:
            right_uncs = l2 if r1 is None else (r1 if l2 is None else r1+l2)
            result.set_columns(right_unc=right_uncs)

        return result
    
    def __mul__(self, other: Union[Score, Self]) -> Self:
        keys, (v1, l1, r1), (v2, l2, r2) = self._result_keys(other)
        keynames = list(keys.keys())
        values = v1*v2
        result = type(self)(keys, 
            keynames=keynames, columns=keynames,
            default_score=self._result_default_score(other, Score.__mul__),
        )
        result.set_columns(value=values)

        if l1 is None and r1 is None and l2 is None and r2 is None:
            return result
        
        l1 = 0 if l1 is None else l1
        r1 = 0 if r1 is None else r1
        l2 = 0 if l2 is None else l2
        r2 = 0 if r2 is None else r2

        extremes = np.stack([
            (v1 - l1) * (v2 - l2), (v1 - l1) * (v2 + r2),
            (v1 + r1) * (v2 - l2), (v1 + r1) * (v2 + r2),
        ])
        result.set_columns(left_unc=values - extremes.min(axis=0))
        result.set_columns(right_unc=extremes.max(axis=0) - values)

        return result
    
    def __truediv__(self, other: Union[Score, Self]) -> Self:
        keys, (v1, l1, r1), (v2, l2, r2) = self._result_keys(other)
        keynames = list(keys.keys())

        result = type(self)(keys, 
            keynames=keynames, columns=keynames,
            default_score=self._result_default_score(other, Score.__truediv__),
        )

        if l1 is None and r1 is None and l2 is None and r2 is None:
            result.set_columns(value=v1/v2)
            return result
        
        l1 = 0 if l1 is None else l1
        r1 = 0 if r1 is None else r1
        l2 = 0 if l2 is None else l2
        r2 = 0 if r2 is None else r2

        if l2 is None and r2 is None:
            values = v1 / v2
        else:
            values = np.where((v2 - l2) * (v2 + r2) > 0, v1 / v2, np.nan)

        extremes = np.stack([
            (v1 - l1) / (v2 - l2), (v1 - l1) / (v2 + r2),
            (v1 + r1) / (v2 - l2), (v1 + r1) / (v2 + r2),
        ])
        result.set_columns(
            values=values,
            left_unc=values - extremes.min(axis=0),
            right_unc=extremes.max(axis=0) - values
        )
        return result

    def abs(self) -> Self:
        if "left_unc" not in self.columns and "right_unc" not in self.columns:
            return self.add_columns(value=np.abs(self.value))
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


class _Njit:
    @staticmethod
    def common_keys_tuples(
        keynames1: list[str], keynames2: list[str],
        keys1: tuple[NDArray, ...], keys2: tuple[NDArray, ...],
    ) -> tuple[
        list[str], # common_keynames
        set[tuple[Hashable, ...]], # common_keys_tuples
    ]:
        common_keynames = list(set(keynames1) & set(keynames2))
        common_keyname_indices1 = [keynames1.index(kn) for kn in common_keynames]
        common_keyname_indices2 = [keynames2.index(kn) for kn in common_keynames]
        n_common_keynames = len(common_keynames)
        if len(keys1) == 0 or len(keys2) == 0:
            return common_keynames, set()
        n_keys1, n_keys2 = len(keys1[0]), len(keys2[0])
        return common_keynames, {
            tuple(keys1[common_keyname_indices1[i]][j] for i in range(n_common_keynames)) 
            for j in range(n_keys1)
        } | {
            tuple(keys2[common_keyname_indices2[i]][j] for i in range(n_common_keynames))
            for j in range(n_keys2)
        }

    @staticmethod
    def indices(
        keynames1: list[str], keynames2: list[str],
        keys1: tuple[NDArray, ...], keys2: tuple[NDArray, ...],
        all_indices1: NDArray[np.int64], all_indices2: NDArray[np.int64],
        keys_indices1: list[tuple[NDArray[np.int64], list[NDArray[np.int64]]]],
        keys_indices2: list[tuple[NDArray[np.int64], list[NDArray[np.int64]]]],
    ) -> tuple[
        dict[str, list], # keys
        list[dict[str, Hashable]], # common_keys_list
        NDArray[np.int64], # indices1
        NDArray[np.int64], # indices2
    ]:
        x = _Njit.common_keys_tuples(keynames1, keynames2, keys1, keys2)
        common_keynames, common_keys_tuples = x

        keynames = list(set(keynames1) | set(keynames2))
        keys = {keyname: list() for keyname in keynames}
        common_keys_list, indices1, indices2 = list(), list(), list()
        keyname_indices1 = {keyname: index for index, keyname in enumerate(keynames1)}
        keyname_indices2 = {keyname: index for index, keyname in enumerate(keynames2)}
        args = (
            keyname_indices1, keyname_indices2, keys1, keys2, keynames, 
            keys, common_keys_list, indices1, indices2
        )
        
        for common_keys_tuple in common_keys_tuples:
            common_keys = dict(zip(common_keynames, common_keys_tuple))
            common_hashed_keys = np.array([hash(k) for k in common_keys_tuple], dtype=np.int64)
            commons = common_keynames, common_hashed_keys
            if len(keynames1) == 0 or len(all_indices1) == 0:
                subindices1 = np.arange(0)
            else:
                subindices1 = _Njit.filters(keynames1, all_indices1, keys_indices1, *commons)
            if len(keynames2) == 0 or len(all_indices2) == 0:
                subindices2 = np.arange(0)
            else:
                subindices2 = _Njit.filters(keynames2, all_indices2, keys_indices2, *commons)

            for i1, i2 in itertools.product(subindices1, subindices2):
                _Njit.append(i1, i2, common_keys, *args)

            if set(keynames2).issubset(common_keynames) and len(subindices2) == 0:
                for i1 in subindices1:
                    _Njit.append(i1, np.int64(-1), common_keys, *args)

            if set(keynames1).issubset(common_keynames) and len(subindices1) == 0:
                for i2 in subindices2:
                    _Njit.append(np.int64(-1), i2, common_keys, *args)
        
        return keys, common_keys_list, np.array(indices1), np.array(indices2)

    @staticmethod
    def append(
        i1: np.int64, i2: np.int64, common_keys: dict[str, Hashable],
        keyname_indices1: dict[str, int], keyname_indices2: dict[str, int],
        keys1: tuple[NDArray, ...], keys2: tuple[NDArray, ...], keynames: list[str],
        keys: dict[str, list], common_keys_list: list[dict[str, Hashable]],
        indices1: list[np.int64 | int], indices2: list[np.int64 | int],
    ):
        indices1.append(i1)
        indices2.append(i2)
        common_keys_list.append(common_keys)
        for keyname in keynames:
            if keyname in common_keys:
                key = common_keys[keyname]
            elif keyname in keyname_indices1:
                key = keys1[keyname_indices1[keyname]][i1]
            else:
                key = keys2[keyname_indices2[keyname]][i2]
            keys[keyname].append(key)

    @staticmethod
    def filters(
        keynames: list[str], all_indices: NDArray[np.int64],
        keys_indices: list[tuple[NDArray[np.int64], list[NDArray[np.int64]]]],
        common_keynames: list[str], common_hashed_keys: NDArray[np.int64], 
    ) -> NDArray[np.int64]:
        common_keynames_indices = [keynames.index(kn) for kn in common_keynames]
        for _, l in keys_indices:
            if len(l) == 0:
                return np.arange(0)
        # return _Njit.f(all_indices, keys_indices, common_hashed_keys, common_keynames_indices)
        indices = all_indices.astype(np.int64)
        for i, hashed_key in enumerate(common_hashed_keys):
            # indices = _Njit.f(i, indices)
            hashed_keys, indices_list = keys_indices[common_keynames_indices[i]]
            key_indices = np.where(hashed_keys == hashed_key)[0]
            if len(key_indices) == 0:
                return np.arange(0)
            indices = np.intersect1d(indices, indices_list[key_indices[0]].astype(np.int64))
        return indices
    
    # @staticmethod
    # @njit
    # def f(
    #     all_indices: NDArray[np.int64],
    #     keys_indices: list[tuple[NDArray[np.int64], list[NDArray[np.int64]]]],
    #     common_hashed_keys: NDArray[np.int64], 
    #     common_keynames_indices: NDArray[np.int64],
    # ) -> NDArray[np.int64]:
    #     indices = all_indices
    #     for i, hashed_key in enumerate(common_hashed_keys):
    #         hashed_keys, indices_list = keys_indices[common_keynames_indices[i]]
    #         key_indices = np.where(hashed_keys == hashed_key)[0]
    #         if len(key_indices) == 0:
    #             return np.arange(0)
    #         indices = np.intersect1d(indices, indices_list[key_indices[0]])
    #     return indices