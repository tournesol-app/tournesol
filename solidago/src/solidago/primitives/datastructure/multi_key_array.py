from typing import Callable, Iterable, Self

import numpy as np
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

    def iter(self) -> Iterable[tuple]:
        return self.to_df().itertuples(index=False)

    def to_df(self) -> pd.DataFrame:
        return self.dataset.stack(index=[...]).dropna("index").as_numpy().to_dataframe()

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


class Objects(MultiKeyArray):
    KEY_NAMES = ["id"]

    @classmethod
    def from_dict(cls, data: dict[tuple, tuple], sparse=True, vector_dims=0):
        objects = super().from_dict(data, sparse)
        if vector_dims > 0:
            objects.dataset["vector"] = (
                cls.KEY_NAMES + ["vector_dim"],
                np.zeros((objects.n_objects, vector_dims)),
            )
        return objects

    @property
    def n_objects(self):
        return len(self.dataset["id"])

    @property
    def vectors(self):
        return self.dataset["vector"].to_numpy()

    def values(self, key: str):
        if key not in self.VALUE_NAMES:
            raise ValueError(f"Unknown field {key!r}")
        return self.dataset[key].to_numpy()

    def keys(self) -> np.ndarray:
        return self.dataset["id"].values

    def sample(self, n_items: int, replace=False) -> Self:
        sample_ids = np.random.choice(self.dataset["id"], size=n_items, replace=replace)
        return self.where(lambda x: x["id"].isin(sample_ids))

    def assign(self, **kwargs):
        for (key, values) in kwargs.items():
            if key not in self.VALUE_NAMES:
                raise ValueError(f"Unknown field {key!r}")
            if isinstance(values, (list, np.ndarray)):
                self.dataset[key] = (
                    self.KEY_NAMES,
                    values
                )
            else:
                self.dataset[key] = values
        return self

    def id_to_idx(self) -> dict:
        return {id: idx for (idx, id) in enumerate(self.dataset["id"].values)}

    def __len__(self):
        return len(self.dataset["id"])

    def __getitem__(self, key):
        return self.dataset.sel(id=key)

    @classmethod
    def load(cls, directory: str, name: str, id_column: str | None = None):
        if not name.endswith(".csv"):
            name = f"{name}.csv"
        filename = f"{directory}/{name}"
        df = pd.read_csv(filename, keep_default_na=False)
        if id_column is not None:
            df.index = df[id_column]
        df.index.name = "id"
        dataset = Dataset.from_dataframe(df, sparse=False)
        return cls(dataset)


class Vouches(MultiKeyArray):
    KEY_NAMES = ["by", "to", "kind"]
    VALUE_NAMES = ["weight", "priority"]


class Users(Objects):
    VALUE_NAMES = ["username", "is_pretrusted", "trust"]

    @classmethod
    def range(cls, n: int, vector_dims=0):
        return cls.from_dict(
            {(idx,): ("", False, 0.0) for idx in range(n)},
            sparse=False,
            vector_dims=vector_dims,
        )

    @classmethod
    def from_usernames(cls, usernames: list[str]):
        return cls.from_dict({
            (username,): (username, False, 0.0)
            for username in usernames
        })

    @classmethod
    def load(cls, directory: str, name: str, id_column: str | None = "username"):
        return super().load(directory=directory, name=name, id_column=id_column)
        