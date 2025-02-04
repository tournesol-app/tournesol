from abc import ABC, abstractmethod
from typing import Union, Optional, Callable, Any, Iterable
from types import BuiltinFunctionType, SimpleNamespace
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce

import pandas as pd


class UnnamedDataFrame(DataFrame):
    def __init__(self, 
        key_names: Optional[Union[str, list[str]]]=None, 
        value_names: Optional[Union[str, list[str]]]=None,
        save_filename: Optional[str]=None, 
        default_value: Optional[Any]=None,
        *args, 
        **kwargs
    ):
        """ Defines a DataFrame wrapper """
        super().__init__(*args, **kwargs)
        to_list = lambda l: [l] if isinstance(l, str) else l
        self.meta = SimpleNamespace()
        self.meta.save_filename = save_filename
        self.meta.key_names, self.meta.value_names = to_list(key_names), to_list(value_names)
        assert isinstance(self.key_names, list) or not self.key_names
        assert isinstance(self.value_names, list) or not self.value_names
        columns = sum([ n if n else list() for n in (self.key_names, self.value_names) ], list())
        for column in columns:
            if column not in self.columns:
                self[column] = float("nan")
        self.meta.save_filename = save_filename
        self.meta._default_value = default_value
        
    @property
    def key_names(self):
        return self.meta.key_names
        
    @property
    def value_names(self):
        return self.meta.value_names
    
    @property
    def save_filename(self):
        return self.meta.save_filename
    
    """ The following methods could be worth redefining in derived classes """
    def default_value(self) -> Any:
        return self.meta._default_value
    
    def value2row(self, value: Any, **kwargs) -> Series:
        return Series(kwargs | dict(value))
    
    def row2key(self, row: Series) -> Any:
        if not self.key_names:
            return row
        if len(self.key_names) == 1:
            return row[self.key_names[0]]
        return [ row[name] for name in self.key_names ]
        
    def row2value(self, row: Series) -> Any:
        if not self.value_names:
            return row
        if len(self.value_names) == 1:
            return row[self.value_names[0]]
        return [ row[name] for name in self.value_names ]
    
    def df2value(self, df: DataFrame) -> Any:
        return df
        
    """ The following methods are are more standard """
    def add_row(self, value: Optional[Any]=None, **kwargs) -> None:
        self.index = list(range(len(self)))
        self.loc[len(self)] = self.value2row(value, **kwargs) if value else Series(kwargs)
    
    def get(self, process: bool=False, last_only: bool=False, **kwargs) -> "UnnamedDataFrame":
        fltr = True
        for column, value in kwargs.items():
            fltr &= (self[column] == value)
        df = self[fltr]
        if not process:
            return type(self)(df)
        if df.empty:
            return self.default_value()
        if last_only:
            return self.row2value(df.iloc[-1])
        return self.df2value(df)

    def __contains__(self, **kwargs) -> bool:
        return not self.get(**kwargs).empty

    def set(self, value: Optional[Any]=None, **kwargs) -> None:
        df = self,get(process=False, **kwargs)
        if df.empty:
            self.add_row(value, **kwargs)
        else: # Updates the last row of df
            df.iloc[-1] = self.value2row(value, **kwargs)

    def __or__(self, other: "UnnamedDataFrame") -> "UnnamedDataFrame":
        return type(self)(pd.concat([self, other]))
    
    @classmethod
    def load(cls, filename: str) -> "UnnamedDataFrame":
        try: return cls(pd.read_csv(filename, keep_default_na=False))
        except pd.errors.EmptyDataError: return cls()

    def iter(self, columns: Optional[list[str]]=None, process: bool=True) -> Iterable:
        columns = columns if columns else self.key_names
        if columns is None:
            for _, row in self.iterrows():
                if process:
                    yield self.row2key(row), self.row2value(row)
                else:
                    yield row
            return None            
        if not columns:
            yield list(), self.df2value(self) if process else self
            return None
        groups = DataFrame(self).groupby(columns)
        key_names = [ n for n in self.key_names if n not in columns ]
        for key in list(groups.groups.keys()):
            yield key, type(self)(groups.get_group(key), key_names=key_names)

    def __iter__(self, process: bool=True) -> Iterable:
        return self.iter(process=process)

    def keys(self, columns: Optional[list[str]]=None) -> list:
        return [ keys for keys, _ in self.iter(columns=columns, process=True) ]

    def values(self, process: bool=True) -> list:
        return [ value for _, value in self ]
        
    def save(self, directory: Union[str, Path]) -> tuple[str, str]:
        assert self.save_filename is not None, f"{type(self).__name__} has no save filename"
        path = Path(directory) / self.save_filename
        self.to_csv(path, index=False)
        return type(self).__name__, str(path)

