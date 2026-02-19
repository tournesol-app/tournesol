from collections import namedtuple
from typing import Callable, Iterable, Self, NamedTuple

import pandas as pd
import xarray as xr


class MultiKeyArray:
    KEY_NAMES: list[str]
    VALUE_NAMES: list[str]

    def __init__(self, dataset: xr.Dataset) -> None:
        self.dataset = dataset

    @classmethod
    def from_dataframe(cls, df: pd.DataFrame, sparse: bool = False) -> Self:
        # Ensure the index matches our expected keys
        if not all(k in df.index.names for k in cls.KEY_NAMES):
            # If keys are columns, set them as index
            df = df.set_index(cls.KEY_NAMES)

        dataset = xr.Dataset.from_dataframe(df, sparse=sparse)
        return cls(dataset)

    @classmethod
    def from_dict(cls, data: dict[tuple, tuple], sparse=True):
        df = pd.DataFrame.from_dict(data, orient="index", columns=cls.VALUE_NAMES)
        df.index = pd.MultiIndex.from_tuples(df.index, names=cls.KEY_NAMES)
        return cls.from_dataframe(df, sparse=sparse)

    @classmethod
    def load(cls, directory: str, name: str, **kwargs):
        if not name.endswith(".csv"):
            name = f"{name}.csv"
        filename = f"{directory}/{name}"
        df = pd.read_csv(filename, keep_default_na=False, index_col=cls.KEY_NAMES)
        return cls.from_dataframe(df, sparse=False)

    def filter(self, **kwargs) -> Self:
        """Fast coordinate-based selection."""
        return type(self)(dataset=self.dataset.sel(indexers=kwargs))

    def where(self, filter_fun: Callable):
        return type(self)(dataset=self.dataset.where(filter_fun, drop=True))

    def to_dataframe(self) -> pd.DataFrame:
        return self._get_stacked_dataset().as_numpy().to_dataframe()

    def merge(self, other: Self) -> Self:
        return type(self)(xr.merge([self.dataset, other.dataset]))

    def iter(self) -> Iterable[NamedTuple]:
        Row = namedtuple("Row", self.KEY_NAMES + self.VALUE_NAMES)
        stacked = self._get_stacked_dataset().as_numpy()
        return (
            Row(*items)
            for items in zip(*(stacked[n].values for n in (self.KEY_NAMES + self.VALUE_NAMES)))
        )

    def _get_stacked_dataset(self) -> xr.Dataset:
        return self.dataset.stack(index=[...], create_index=False).dropna("index")
