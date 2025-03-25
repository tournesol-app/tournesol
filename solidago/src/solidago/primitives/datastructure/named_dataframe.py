from typing import Union, Optional, Iterable
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
        if self.index.name is None and len(self.columns) == 1 and self.columns[0] == 0:
            self.rename(columns={ self.columns[0]: self.index_name }, inplace=True)
        if self.index_name in self.columns:
            self.set_index(self.index_name, inplace=True)
        self.index = [str(name) for name in self.index]
        self.index.name = self.index_name
        self.meta._name2index = None

    @property
    def save_filename(self):
        return self.meta.save_filename
    
    @property
    def name2index(self):
        if self.meta._name2index is None:
            self.meta._name2index = { str(name): i for i, name in enumerate(self.index) }
        return self.meta._name2index

    @save_filename.setter
    def save_filename(self, save_filename: Union[Path, str]):
        self.meta.save_filename = save_filename

    @classmethod
    def load(cls, directory: str, df_name: str):
        return cls(pd.read_csv(f"{directory}/{df_name}", keep_default_na=False))

    def save(self, directory: Union[Path, str]) -> tuple[str, dict]:
        path = Path(directory) / self.save_filename
        self.to_csv(path)
        return type(self).__name__, dict(df_name=self.save_filename)

    def get(self, 
        key: Union[str, NamedSeries, Iterable, dict],
        ignore_missing_keys: bool=True
    ) -> Union[NamedSeries, "NamedDataFrame"]:
        """ Extract carefully typed objects given index names (default) or attributes
        
        Returns
        -------
        out: NamedSeries or NamedDataFrame
            If key is a string or a NamedSeries, returns corresponding NamedSeries
            If key is a set/list/tuple, returns NamedDataFrame with matching indices
            If key is a dict, returns NamedDataFrame with matching attributes
        """
        if isinstance(key, (str, NamedSeries)):
            return self.series_cls(self.loc[str(key)])
        if isinstance(key, dict):
            filtered, key_values = True, key
            for key, value in key_values.items():
                filtered &= (self[key] == value)
            return type(self)(self[filtered])
        keys = [k for k in key if k in self.index] if ignore_missing_keys else list(key)
        return type(self)(self.loc[keys])
    
    def __iter__(self) -> Iterable:
        for _, row in self.iterrows():
            yield self.series_cls(row)
    
    def __repr__(self) -> str:
        return repr(DataFrame(self))
    
    def __contains__(self, series: Union[str, NamedSeries]):
        return str(series) in set(self.index)

    def __bool__(self) -> bool:
        return not self.empty
