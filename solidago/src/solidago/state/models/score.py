import math
import numbers

from typing import Optional, Union, Any, Callable
from pandas import Series, DataFrame

from solidago.primitives.datastructure import UnnamedDataFrame


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


class MultiScore(UnnamedDataFrame):
    def __init__(self, 
        data: Optional[Any]=None, 
        key_names: list[str]=["criterion"], 
        value_names: list[str]=["value", "left_unc", "right_unc"],
        name: str="multiscore",
        default_value: Score=Score.nan(),
        last_only: bool=True,
        **kwargs
    ):
        """ We consider the possibility of multidimensional scoring.
        In the context of Tournesol, for instance, the dimensions are the criteria.
        For scientific peer reviewing, it could be the criteria may be
        {'clarity', 'correctness', 'originality', 'rating'}. """
        super().__init__(data, key_names, value_names, name, default_value, last_only, **kwargs)
    
    def row2value(self, row: Series) -> Any:
        return Score(row["value"], row["left_unc"], row["right_unc"])
    
    def input2dict(self, *args, keys_only: bool=False, **kwargs) -> dict:
        key_value_columns = self.key_names if keys_only else (self.key_names + self.value_names)
        if keys_only:
            args = args[:len(self.key_names)]
        assert len(args) <= len(key_value_columns) + 3
        assert all({ key not in key_value_columns[:len(args)] for key in kwargs })
        f = lambda v, k: str(v) if k in self.key_names else v
        kwargs = { k: f(v, k) for k, v in kwargs.items() if (not keys_only or k in self.key_names) }
        args_key_names = [ kn for kn in self.key_names if kn not in kwargs ]
        kwargs |= { k: f(v, k) for k, v  in zip(args_key_names, args[:len(args_key_names)]) }
        args_values = args[len(args_key_names):]
        if len(args_values) > 0 and isinstance(args_values[0], Score):
            assert "score" not in kwargs
            kwargs["score"] = args_values[0]
            args = args[:-1]
        elif len(args_values) > 0:
            assert "score" not in kwargs
            if len(args_values) == 1:
                args_values = (args_values[0], 0, 0)
            assert len(args_values) == 3, args
            kwargs["score"] = Score(*args_values)
        if "score" in kwargs:
            kwargs["value"] = kwargs["score"].value
            kwargs["left_unc"] = kwargs["score"].left_unc
            kwargs["right_unc"] = kwargs["score"].right_unc
            del kwargs["score"]
        if not self.value_names and len(args) > len(self.key_names):
            assert len(args) == len(self.key_names) + 1
            return kwargs | args[-1].to_dict()
        return kwargs | { k: f(v, k) for k, v in zip(key_value_columns[:len(args)], args) }
    
    @classmethod
    def nan(cls) -> "MultiScore":
        return MultiScore()

    def __eq__(self, other: "MultiScore") -> bool:
        for key in set(self.keys()) | set(other.keys()):
            if self.get(key) != other.get(key):
                return False
        return True
        
    def __neq__(self, other: "MultiScore") -> bool:
        return not (self == other)

    def __neg__(self) -> "MultiScore":
        return MultiScore(
            data=[ 
                (*(key if isinstance(key, tuple) else (key,)), *(- score).to_triplet()) 
                for key, score in self 
            ],
            key_names=self.key_names
        )
    
    def coordinate_wise_operation(self, 
        other: Union[Score, "MultiScore"], 
        score_operation: Callable
    ) -> "MultiScore":
        if isinstance(other, (numbers.Number, Score)):
            return MultiScore(
                data=[ 
                    (
                        *(key if isinstance(key, tuple) else (key,)), 
                        *(score_operation(score, other)).to_triplet()
                    )
                    for key, score in self 
                ],
                key_names=self.key_names
            )
        assert self.key_names == other.key_names
        data = [
            (k if isinstance(k, tuple) else (k,), score_operation(self.get(k), other.get(k))) 
            for k in set(self.keys()) | set(other.keys())
        ]
        return MultiScore(
            data=[(*key, *score.to_triplet()) for key, score in data if not score.isnan()],
            key_names=self.key_names
        )
    
    def __add__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        return self.coordinate_wise_operation(other, Score.__add__)
        
    def __sub__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        return self.coordinate_wise_operation(other, Score.__sub__)
    
    def __mul__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        return self.coordinate_wise_operation(other, Score.__mul__)
        
    def __truediv__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        return self.coordinate_wise_operation(other, Score.__truediv__)
