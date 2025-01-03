from typing import Union, Optional
from pandas import DataFrame, Series
from types import SimpleNamespace
from pathlib import Path

import pandas as pd


class NamedSeries(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = str(self.name)
        self.meta = SimpleNamespace()

    def __hash__(self):
        return hash(self.name)
    
    def __str__(self):
        return str(self.name)


class NamedDataFrame(DataFrame):
    index_name: str
    series_cls: type

    def __init__(self, *args, save_filename: Optional[Union[str, Path]]=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.meta = SimpleNamespace()
        self.meta.save_filename = save_filename
        if len(self.columns) == 1:
            self.rename(columns={ self.columns[0]: self.index_name }, inplace=True)
        if self.index_name in self.columns:
            self.set_index(self.index_name, inplace=True)
        self.index = [str(name) for name in self.index]
        self.index.name = self.index_name

    @property
    def save_filename(self):
        return self.meta.save_filename

    @save_filename.setter
    def save_filename(self, save_filename: Union[Path, str]):
        self.meta.save_filename = save_filename

    @classmethod
    def load(cls, filename: Union[Path, str]):
        return cls(pd.read_csv(filename, keep_default_na=False))

    def save(self, directory: Union[Path, str]) -> tuple[str, str]:
        path = Path(directory) / self.save_filename
        self.to_csv(path)
        return type(self).__name__, str(path)
                
    def get(self, series: Union[str, NamedSeries]) -> NamedSeries:
        assert series in self, (series, self)
        return self.series_cls(self.loc[str(series)])
    
    def extract(self, names: set[str]) -> NamedDataFrame:
        return type(self)(self[self.index.isin(names)], save_filename=self.save_filename)
    
    def __iter__(self):
        for _, row in self.iterrows():
            yield self.series_cls(row)
    
    def __repr__(self):
        return repr(DataFrame(self))
    
    def __contains__(self, series: Union[str, NamedSeries]):
        return str(series) in set(self.index)
