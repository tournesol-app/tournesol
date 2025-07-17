from typing import Self

import numpy as np
import pandas as pd
from xarray import Dataset

from .multi_key_array import MultiKeyArray


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
    def load(cls, directory: str, name: str, id_column: str | None = None, **kwargs):
        if not name.endswith(".csv"):
            name = f"{name}.csv"
        filename = f"{directory}/{name}"
        df = pd.read_csv(filename, keep_default_na=False)
        if id_column is not None:
            df.index = df[id_column]
        df.index.name = "id"
        dataset = Dataset.from_dataframe(df, sparse=False)
        return cls(dataset)
