import math

from typing import Optional, Union, Any

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
            assert isinstance(left_unc, (int, float)) and isinstance(right_unc, (int, float))
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
        return self.to_triplet() == score.to_triplet()
        
    def __neq__(self, score: Union[int, float, "Score"]) -> bool:
        if not isinstance(score, Score):
            score = Score(score, 0, 0)
        return self.to_triplet() != score.to_triplet()
    
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
        name="multiscore",
        last_only=True,
        **kwargs
    ):
        """ We consider the possibility of multidimensional scoring.
        In the context of Tournesol, for instance, the dimensions are the criteria.
        For scientific peer reviewing, it could be the criteria may be
        {'clarity', 'correctness', 'originality', 'rating'}. """
        super().__init__(data, key_names, value_names, name, Score.nan(), last_only, **kwargs)
    
    def row2value(self, row: Series) -> Any:
        return Score(row["value"], row["left_unc"], row["right_unc"])
    
    def input2dict(self, *args, keys_only: bool=False, **kwargs) -> dict:
        key_value_columns = self.key_names if keys_only else (self.key_names + self.value_names)
        if keys_only:
            args = args[:len(self.key_names)]
        assert len(args) <= len(key_value_columns) + 1
        assert all({ key not in key_value_columns[:len(args)] for key in kwargs })
        f = lambda v, k: str(v) if k in self.key_names else v
        if "score" in kwargs:
            kwargs["value"] = kwargs["score"].value
            kwargs["left_unc"] = kwargs["score"].left_unc
            kwargs["right_unc"] = kwargs["score"].right_unc
            del kwargs["score"]
        kwargs = { k: f(v, k) for k, v in kwargs.items() if (not keys_only or k in self.key_names) }
        if not self.value_names and len(args) > len(self.key_names):
            assert len(args) == len(self.key_names) + 1
            return kwargs | args[-1].to_dict()
        return kwargs | { k: f(v, k) for k, v in zip(key_value_columns[:len(args)], args) }
    
    @classmethod
    def nan(cls) -> "MultiScore":
        return MultiScore()

    def __neg__(self) -> "MultiScore":
        return MultiScore(
            data=[ (*tuple(key), *(- score).to_triplet()) for key, score in self ],
            key_names=self.key_names
        )
    
    def __add__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        if isinstance(other, (int, float, Score)):
            return MultiScore(
                data=[ (*tuple(key), *(score + other).to_triplet()) for key, score in self ],
                key_names=self.key_names
            )
        assert self.key_names == other.key_names
        keys = set(self["criterion"]) & set(other["criterion"])
        return MultiScore(
            data=[ (*tuple(key), *(self[key] + other[key]).to_triplet() for key in keys ],
            key_names=self.key_names
        )
    
    def __sub__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        if isinstance(other, (int, float, Score)):
            return MultiScore(
                data=[ (*tuple(key), *(score - other).to_triplet()) for key, score in self ],
                key_names=self.key_names
            )
        assert self.key_names == other.key_names
        keys = set(self["criterion"]) & set(other["criterion"])
        return MultiScore(
            data=[ (*tuple(key), *(self[key] - other[key]).to_triplet() for key in keys ],
            key_names=self.key_names
        )
        
    def __mul__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        if isinstance(other, (int, float, Score)):
            return MultiScore(
                data=[ (*tuple(key), *(score * other).to_triplet()) for key, score in self ],
                key_names=self.key_names
            )
        assert self.key_names == other.key_names
        keys = set(self["criterion"]) & set(other["criterion"])
        return MultiScore(
            data=[ (*tuple(key), *(self[key] * other[key]).to_triplet() for key in keys ],
            key_names=self.key_names
        )
        
    def __truediv__(self, other: Union[Score, "MultiScore"]) -> "MultiScore":
        if isinstance(other, (int, float, Score)):
            return MultiScore(
                data=[ (*tuple(key), *(score / other).to_triplet()) for key, score in self ],
                key_names=self.key_names
            )
        assert self.key_names == other.key_names
        keys = set(self["criterion"]) & set(other["criterion"])
        return MultiScore(
            data=[ (*tuple(key), *(self[key] / other[key]).to_triplet() for key in keys ],
            key_names=self.key_names
        )
