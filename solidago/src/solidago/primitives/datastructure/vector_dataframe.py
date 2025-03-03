from typing import Union, Optional, Iterable
from pandas import DataFrame, Series
from types import SimpleNamespace
from pathlib import Path

import pandas as pd
import numpy as np

from .named_dataframe import NamedSeries, NamedDataFrame

""" The following classes are designed to be Mixin.
This means that they will merely write down vector information,
and pass on through the arguments to another inherited class,
which would inherit from NameDataFrame. """



class VectorSeries(NamedSeries):
    def __init__(self, vector: np.ndarray, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta.vector = vector
    
    @property
    def vector(self) -> np.ndarray:
        return self.meta.vector
    
    @vector.setter
    def vector(self, value) -> None:
        self.meta.vector = value


class VectorDataFrame(NamedDataFrame):
    index_name: str
    series_cls: type

    def __init__(self, 
        vectors: Union[np.ndarray, list[VectorSeries]], 
        save_vector_filename: Optional[Union[str, Path]], 
        *args, **kwargs
    ):
        if isinstance(vectors, np.ndarray) and len(args) == 0 and len(kwargs) == 0:
            args = [list(range(len(vectors)))]
        if isinstance(vectors, list) and all({ isinstance(v, VectorSeries) for v in vectors }):
            kwargs = dict(data=vectors)
            vectors = np.array([v.vector for v in vectors])
        super().__init__(*args, **kwargs)
        assert len(vectors) == len(self), (vectors, self)
        self["vector_index"] = list(range(len(self)))
        self.meta.vectors = vectors
        self.meta.save_vector_filename = save_vector_filename
    
    @property
    def vectors(self) -> np.ndarray:
        return self.meta.vectors
    
    @vectors.setter
    def vectors(self, value: np.ndarray) -> None:
        self.meta.vectors = value
    
    @property
    def save_vector_filename(self) -> str:
        return self.meta.save_vector_filename
    
    @save_vector_filename.setter
    def save_vector_filename(self, value: str) -> None:
        self.meta.save_vector_filename = value

    @classmethod
    def load(cls, directory: Union[Path, str], filenames: tuple[str, str]) -> "VectorDataFrame":
        return cls(
            np.loadtxt(f"{directory}/{filenames[1]}", delimiter=","),
            pd.read_csv(f"{directory}/{filenames[0]}", keep_default_na=False)
        )

    def save(self, directory: Union[Path, str]) -> tuple[str, tuple[str, str]]:
        assert self.meta.save_vector_filename is not None
        vectors_path = Path(directory) / self.meta.save_vector_filename
        np.savetxt(vectors_path, self.vectors, delimiter=",")
        class_name, df_path = super().save(directory)
        return type(self).__name__, (df_path, self.meta.save_vector_filename)

    def get(self, key: Union[str, NamedSeries, Iterable, dict]) -> Union[VectorSeries, "VectorDataFrame"]:
        """ Extract carefully typed objects given index names (default) or attributes
        
        Returns
        -------
        out: NamedSeries or NamedDataFrame
            If key is a string or a NamedSeries, returns corresponding NamedSeries
            If key is a set/list/tuple, returns NamedDataFrame with matching indices
            If key is a dict, returns NamedDataFrame with matching attributes
        """
        if isinstance(key, (str, NamedSeries)):
            row = self.loc[str(key)]
            return self.series_cls(self.vectors[int(row["vector_index"])], row)
        if isinstance(key, dict):
            filtered, key_values = True, key
            for key, value in key_values.items():
                filtered &= (self[key] == value)
            sub_df = self[filtered]
        else:
            assert isinstance(key, (set, tuple, list))
            sub_df = self.loc[list(key)]
        return type(self)(vectors=self.vectors[sub_df["vector_index"]], data=sub_df)
                
    def __iter__(self):
        for _, row in self.iterrows():
            yield self.series_cls(self.vectors[int(row["vector_index"])], row)
        
    def __repr__(self) -> str:
        return repr(DataFrame(self))

    def append(self, series: VectorSeries) -> VectorSeries:
        series["vector_index"] = len(self)
        self._append(series)
        self.vectors = np.vstack([self.vectors, series.vector])
        return self
    
    def delete(self, series: VectorSeries) -> VectorSeries:
        vector_index = self.loc[str(series), "vector_index"]
        self.vectors = np.delete(self.vectors, vector_index, axis=0)
        self.drop(str(series))
        self["vector_index"] = list(range(len(self)))
        return self
