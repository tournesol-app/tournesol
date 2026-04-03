from collections import namedtuple
from typing import Callable, Iterable, Self, NamedTuple

import pandas as pd


class MultiKeyArray:
    KEY_NAMES: list[str]
    VALUE_NAMES: list[str]

    def __init__(self, df: pd.DataFrame) -> None:
        self._df = df.reset_index(drop=True)

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame) -> Self:
        if all(k in df.index.names for k in cls.KEY_NAMES):
            df = df.reset_index()
        return cls(df[cls.KEY_NAMES + cls.VALUE_NAMES])

    @classmethod
    def from_dict(cls, data: dict[tuple, tuple]) -> Self:
        df = pd.DataFrame.from_dict(data, orient="index", columns=cls.VALUE_NAMES)
        df.index = pd.MultiIndex.from_tuples(df.index, names=cls.KEY_NAMES)
        return cls.from_dataframe(df)

    @classmethod
    def load(cls, directory: str, name: str) -> Self:
        if not name.endswith(".csv"):
            name = f"{name}.csv"
        df = pd.read_csv(f"{directory}/{name}", keep_default_na=False)
        return cls.from_dataframe(df)

    # def save(self, directory: str, name: str) -> None:
    #     if not name.endswith(".csv"):
    #         name = f"{name}.csv"
    #     self._df.to_csv(f"{directory}/{name}", index=False)

    def filter(self, **kwargs) -> Self:
        """Exact-match key selection. Supports scalar or list values.

        Example:
            arr.filter(key1="a", key2=["x", "y"])
        """
        mask = pd.Series(True, index=self._df.index)
        for col, val in kwargs.items():
            if isinstance(val, (list, tuple)):
                mask &= self._df[col].isin(val)
            else:
                mask &= self._df[col] == val
        return type(self)(self._df.loc[mask])

    def where(self, filter_fun: Callable[[pd.DataFrame], pd.Series]) -> Self:
        """Row-wise boolean filter using a callable.

        Example:
            arr.where(lambda df: df["value"] > 0)
        """
        return type(self)(self._df.loc[filter_fun(self._df)])

    def assign(self, **kwargs) -> Self:
        """Update one or more VALUE_NAMES columns.

        Accepts scalars, lists, or callables (same contract as pd.DataFrame.assign).
        Keys must be in VALUE_NAMES; assigning to KEY_NAMES is not allowed.

        Example:
            arr.assign(score=0.0)
            arr.assign(score=lambda df: df["score"] * 2)
        """
        invalid = [k for k in kwargs if k not in self.VALUE_NAMES]
        if invalid:
            raise ValueError(
                f"Cannot assign to columns {invalid}. "
                f"Only VALUE_NAMES {self.VALUE_NAMES} are mutable."
            )
        return type(self)(self._df.assign(**kwargs))

    def merge(self, other: Self) -> Self:
        return type(self)(pd.concat([self._df, other._df], ignore_index=True))

    def to_dataframe(self) -> pd.DataFrame:
        return self._df[self.KEY_NAMES + self.VALUE_NAMES].copy()

    def iter(self) -> Iterable[NamedTuple]:
        Row = namedtuple("Row", self.KEY_NAMES + self.VALUE_NAMES)
        return (
            Row(*row)
            for row in self._df[self.KEY_NAMES + self.VALUE_NAMES].itertuples(index=False)
        )

    def __len__(self) -> int:
        return len(self._df)

    def __repr__(self) -> str:
        return f"{type(self).__name__}(n={len(self)})\n{self._df}"
