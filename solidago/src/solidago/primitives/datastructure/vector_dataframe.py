from typing import Union
from pandas import DataFrame, Series
from types import SimpleNamespace
from pathlib import Path

import pandas as pd
import numpy as np

from .named_dataframe import NamedSeries, NamedDataFrame


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
    series_class: type

    def __init__(self, 
        vectors: Union[np.ndarray, list[VectorSeries]], 
        save_filename: Union[str, Path], 
        save_vector_filename: Union[str, Path], 
        *args, 
        **kwargs
    ):
        if len(args) == 0 and len(kwargs) == 0:
            args = [list(range(len(vectors)))]
        if all({ isinstance(v, VectorSeries) for v in vectors }):
            args = [vectors] + list(args)
            vectors = np.array([v.vector for v in vectors])
        super().__init__(*args, save_filename=save_filename, **kwargs)
        assert len(vectors) == len(self)
        self["vector_index"] = list(range(len(self)))
        self.meta.vectors = vectors
        self.meta.save_vector_filename = save_vector_filename
    
    @property
    def vectors(self) -> np.ndarray:
        return self.meta.vectors
    
    @vectors.setter
    def vectors(self, value) -> None:
        self.meta.vectors = value

    @classmethod
    def load(cls, filenames: tuple[str, str]) -> "VectorDataFrame":
        return cls(
            np.loadtxt(filenames[1], delimiter=","),
            pd.read_csv(filenames[0], keep_default_na=False)
        )

    def save(self, directory) -> tuple[str, tuple[str, str]]:
        vectors_path = Path(directory) / self.meta.save_vector_filename
        np.savetxt(vectors_path, self.vectors, delimiter=",")
        class_name, df_path = super(VectorDataFrame, self).save(directory)
        return type(self).__name__, (df_path, str(vectors_path))

    def get(self, series: Union[str, NamedSeries]) -> VectorSeries:
        assert str(series) in self.index, (series, self)
        row = self.loc[str(series)]
        return VectorSeries(self.vectors[row["vector_index"]], row)
        
    def __iter__(self):
        for _, row in self.iterrows():
            yield self.series_class(self.vectors[row["vector_index"]], row)
        
    def __repr__(self) -> str:
        return repr(DataFrame(self)) + "\n\n" + repr(self.vectors)

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
