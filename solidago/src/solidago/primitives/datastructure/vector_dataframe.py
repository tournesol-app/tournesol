from typing import Union, Iterable
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
        save_vector_filename: Union[str, Path], 
        *args, 
        **kwargs
    ):
        if len(args) == 0 and len(kwargs) == 0:
            args = [list(range(len(vectors)))]
        if isinstance(vectors, list) and all({ isinstance(v, VectorSeries) for v in vectors }):
            args = [vectors] + list(args)
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
    def vectors(self, value) -> None:
        self.meta.vectors = value

    @classmethod
    def load(cls, filenames: tuple[str, str]) -> "VectorDataFrame":
        return cls(
            np.loadtxt(filenames[1], delimiter=","),
            pd.read_csv(filenames[0], keep_default_na=False)
        )

    def save(self, directory: Union[Path, str]) -> tuple[str, tuple[str, str]]:
        vectors_path = Path(directory) / self.meta.save_vector_filename
        np.savetxt(vectors_path, self.vectors, delimiter=",")
        class_name, df_path = super(VectorDataFrame, self).save(directory)
        return type(self).__name__, (df_path, str(vectors_path))

    def get(self, series: Union[str, NamedSeries]) -> VectorSeries:
        assert str(series) in self.index, (series, self)
        row = self.loc[str(series)]
        return VectorSeries(self.vectors[row["vector_index"]], row)

    def extract(self, names: Iterable[str]) -> "VectorDataFrame":
        sub_df = self.loc[list(names)]
        return type(self)(
            vectors[sub_df["vector_index"]], 
            self.save_vector_filename, 
            sub_df, 
            save_filename=self.save_filename
        )
                
    def __iter__(self):
        for _, row in self.iterrows():
            yield self.series_cls(self.vectors[row["vector_index"]], row)
        
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
