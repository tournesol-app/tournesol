from typing import Callable, Iterable, Self, NamedTuple

import pandas as pd
import xarray as xr
from xarray import Dataset


class MultiKeyArray:
    KEY_NAMES: list[str]
    VALUE_NAMES: list[str]

    def __init__(self, dataset: Dataset) -> None:
        self.dataset = dataset

    @classmethod
    def from_dict(cls, data: dict[tuple, tuple], sparse=True):
        df = pd.DataFrame.from_dict(data, orient="index", columns=cls.VALUE_NAMES)
        df.index = pd.MultiIndex.from_tuples(df.index, names=cls.KEY_NAMES)
        dataset = Dataset.from_dataframe(df, sparse=sparse)
        return cls(dataset)

    def filter(self, **kwargs):
        return type(self)(dataset=self.dataset.sel(indexers=kwargs))

    def where(self, filter_fun: Callable):
        return type(self)(dataset=self.dataset.where(filter_fun, drop=True))

    def iter(self) -> Iterable[NamedTuple]:
        return self.to_df().itertuples(index=False)

    def to_df(self) -> pd.DataFrame:
        return self.dataset.stack(index=[...], create_index=False).dropna("index").as_numpy().to_dataframe()

    @classmethod
    def load(cls, directory: str, name: str, **kwargs):
        if not name.endswith(".csv"):
            name = f"{name}.csv"
        filename = f"{directory}/{name}"
        df = pd.read_csv(filename, keep_default_na=False, index_col=cls.KEY_NAMES)
        dataset = Dataset.from_dataframe(df, sparse=False)
        return cls(dataset)

    def merge(self, other: Self):
        return type(self)(xr.merge([self.dataset, other.dataset]))
