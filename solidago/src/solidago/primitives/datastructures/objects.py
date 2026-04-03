from typing import Self

import numpy as np
import pandas as pd
from xarray import Dataset

from .multi_key_array import MultiKeyArray


class Objects(MultiKeyArray):
    KEY_NAMES = ["id"]

    def __init__(self, df: pd.DataFrame) -> None:
        super().__init__(df)
        self._df.set_index("id", drop=False, inplace=True)
        self._vectors = pd.DataFrame(index=df["id"])

    @classmethod
    def from_dict(cls, data: dict[tuple, tuple], vector_dims=0):
        objects = super().from_dict(data)
        if vector_dims > 0:
            objects._vectors = pd.DataFrame(
                index=objects.keys(),
                data=np.zeros((objects.n_objects, vector_dims))
            )
        return objects

    @property
    def n_objects(self):
        return len(self)

    @property
    def vectors(self):
        return self._vectors.to_numpy()

    def values(self, field: str) -> pd.Series:
        if field not in self.VALUE_NAMES:
            raise ValueError(f"Unknown field {field!r}")
        return pd.Series(index=self._df["id"], data=self._df[field])

    def keys(self) -> np.ndarray:
        return self._df["id"].to_numpy()

    def sample(self, n_items: int, replace=False) -> Self:
        sample_ids = np.random.choice(self.keys(), size=n_items, replace=replace)
        return self.filter(id=sample_ids)

    # def __getitem__(self, key):
    #     return self._df.where

    # @classmethod
    # def load(cls, directory: str, name: str, id_column: str | None = None, **kwargs):
    #     if not name.endswith(".csv"):
    #         name = f"{name}.csv"
    #     filename = f"{directory}/{name}"
    #     df = pd.read_csv(filename, keep_default_na=False)
    #     if id_column is not None:
    #         df.index = df[id_column]
    #     df.index.name = "id"
    #     dataset = Dataset.from_dataframe(df, sparse=False)
    #     return cls(dataset)
