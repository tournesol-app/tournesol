from abc import ABC, abstractmethod
from typing import Union, Optional, Callable, Any, Iterable
from types import BuiltinFunctionType, SimpleNamespace
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce

import pandas as pd


class UnnamedDataFrame(DataFrame):
    row_cls: Optional[type]=None
    
    def __init__(self, 
        data: Optional[Any]=None,
        key_names: Optional[Union[str, list[str]]]=None, 
        value_names: Optional[Union[str, list[str]]]=None,
        name: Optional[str]=None, 
        default_value: Optional[Any]=None,
        last_only: bool=False,
        default_keys: Optional[dict]=None,
        *args, 
        **kwargs
    ):
        """ Defines a DataFrame wrapper """
        def to_list(l):
            if l is None:
                return list()
            elif isinstance(l, str):
                return [l]
            else: 
                return l
        key_names, value_names = to_list(key_names), to_list(value_names)
        key_value_columns = key_names + value_names
        if isinstance(data, list):
            kwargs["columns"] = kwargs["columns"] if "columns" in kwargs else key_value_columns
        super().__init__(data=data, *args, **kwargs)
        if default_keys is not None:
            assert isinstance(default_keys, dict)
            for key, value in default_keys.items():
                if key not in self.columns:
                    self[key] = value
        self.meta = SimpleNamespace()
        self.meta.name = name
        self.meta.key_names, self.meta.value_names = key_names, value_names
        assert isinstance(self.key_names, list) or not self.key_names
        assert isinstance(self.value_names, list) or not self.value_names
        for column in key_value_columns:
            if column not in self.columns:
                self[column] = "NaN"
        self.meta._default_value = default_value
        self.meta._last_only = last_only
        self.meta._group_cache = dict()
        
    @property
    def key_names(self):
        return self.meta.key_names
        
    @property
    def value_names(self):
        return self.meta.value_names
    
    """ The following methods could be worth redefining in derived classes """
    def default_value(self, **kwargs) -> Any:
        return self.meta._default_value
    
    def row2key(self, row: Series) -> Any:
        if not self.key_names:
            return row
        if len(self.key_names) == 1:
            return row[self.key_names[0]]
        return [ row[name] for name in self.key_names ]
        
    def row2value(self, row: Series) -> Any:
        if not self.value_names:
            return row if self.row_cls is None else self.row_cls(row)
        if len(self.value_names) == 1:
            return row[self.value_names[0]]
        return tuple( row[name] for name in self.value_names )
    
    def df2value(self, df: DataFrame, last_only: Optional[bool]=None) -> Any:
        last_only = self.meta._last_only if last_only is None else last_only
        if last_only:
            return self.row2value(df.iloc[-1])
        return type(self)(df)
        
    """ The following methods are are more standard """
    def input2dict(self, *args, keys_only: bool=False, **kwargs) -> dict:
        """ args is assumed to list keys and then values, 
        though some may be specified through kwargs """
        key_value_columns = self.key_names if keys_only else (self.key_names + self.value_names)
        if keys_only:
            args = args[:len(self.key_names)]
        assert len(args) <= len(key_value_columns) + 1
        assert all({ key not in key_value_columns[:len(args)] for key in kwargs })
        f = lambda v, k: str(v) if k in self.key_names else v
        kwargs = { k: f(v, k) for k, v in kwargs.items() if (not keys_only or k in self.key_names) }
        if not self.value_names and len(args) > len(self.key_names):
            assert len(args) == len(self.key_names) + 1
            return kwargs | dict(args[-1])
        return kwargs | { k: f(v, k) for k, v in zip(key_value_columns[:len(args)], args) }
    
    def get(self, 
        *args, 
        process: bool=True, 
        last_only: Optional[bool]=None,
        cache_groups: bool=False,
        **kwargs
    ) -> Union["UnnamedDataFrame", tuple]:
        kwargs = self.input2dict(*args, keys_only=True, **kwargs)
        if cache_groups:
            return self.groupby(list(kwargs.keys()), process=process).get(
                process=process, 
                last_only=last_only, 
                **kwargs
            )
        df = self[reduce(lambda a, x: a & x, [ self[k] == v for k, v in kwargs.items() ], True)]
        other_key_names = [ key_name for key_name in self.key_names if key_name not in kwargs ]
        if other_key_names or not process:
            return type(self)(df, key_names=other_key_names)
        return self.default_value(**kwargs) if df.empty else self.df2value(df, last_only)

    def __contains__(self, *args, **kwargs) -> bool:
        return not self.get(*args, process=False, **kwargs).empty

    def __or__(self, other: "UnnamedDataFrame") -> "UnnamedDataFrame":
        if self.empty:
            data = other
        elif other.empty:
            data = self
        else:
            data = pd.concat([self, other])
            data.index = range(len(data))
        return type(self)(data=data, key_names=self.key_names)

    def delete(self, *args, **kwargs) -> "UnnamedDataFrame":
        kwargs = self.input2dict(*args, keys_only=True, **kwargs)
        indices = self.get(process=False, last_only=False, cache_groups=False, **kwargs)
        self_with_deletion = type(self)(data=self.drop(indices), key_names=self.key_names)
        self_with_deletion.index = range(len(self_with_deletion))
        self.meta._group_cache = dict()
        return self_with_deletion
    
    def add_row(self, *args, **kwargs) -> None:
        self.index = list(range(len(self)))
        d = self.input2dict(*args, **kwargs)
        self.loc[len(self), list(d.keys())] = list(d.values())
        self.meta._group_cache = dict()
        
    def set(self, *args, **kwargs) -> None:
        """ args is assumed to list keys and then values, 
        though some may be specified through kwargs """
        kwargs_keys_only = self.input2dict(*args, keys_only=True, **kwargs)
        kwargs = self.input2dict(*args, **kwargs)
        df = self.get(process=False, **kwargs_keys_only)
        if df.empty:
            self.add_row(**kwargs)
        else: # Updates the last row of df
            name = df.iloc[-1].name
            self.loc[name] = Series(kwargs)
        self.meta._group_cache = dict()

    @classmethod
    def load(cls, 
        filename: Optional[Union[str, Path, "UnnamedDataFrame"]]=None, 
        *args, **kwargs
    ) -> "UnnamedDataFrame":
        if isinstance(filename, UnnamedDataFrame):
            return cls(data=filename, *args, **kwargs)
        try: 
            return cls(pd.read_csv(filename, keep_default_na=False), *args, **kwargs)
        except (pd.errors.EmptyDataError, ValueError):
            return cls(*args, **kwargs)

    def last_only(self) -> "UnnamedDataFrame":
        return type(self)(
            data=DataFrame([ df.iloc[-1] for _, df in self.iter(process=False, last_only=True) ]),
            key_names=self.key_names,
            last_only=True
        )

    def groupby(self, columns: Optional[list[str]]=None, process: bool=True) -> "UnnamedDataFrameDict":
        columns = columns if columns else self.key_names
        if (columns, process) in self.meta._group_cache:
            return self.meta._group_cache[columns, process]
        data = { key: value for key, value in self.iter(columns, process) }
        sub_key_names = [ key for key in self.key_names if key not in columns ]
        from solidago.primitives.datastructure import UnnamedDataFrameDict
        self.meta._group_cache[columns, process] = UnnamedDataFrameDict(
            data, 
            df_cls=type(self), 
            main_key_names=columns, 
            sub_key_names=sub_key_names
        )
        return self.meta._group_cache[columns, process]
    
    def iter(self, 
        columns: Optional[list[str]]=None, 
        process: bool=True, 
        last_only: Optional[bool]=None
    ) -> Iterable:
        last_only = self.meta._last_only if last_only is None else last_only
        columns = self.key_names if columns is None else columns
        if not columns:
            yield list(), self.df2value(self, last_only) if process else self
            return None
        groups = DataFrame(self).groupby(columns)
        kn = [ n for n in self.key_names if n not in columns ]
        for key in list(groups.groups.keys()):
            key_tuple = key if isinstance(key, tuple) else (key, )
            df = groups.get_group(key_tuple)
            if len(kn) > 0 or not process:
                df = DataFrame([df.iloc[-1]]) if last_only and len(kn) == 0 else df
                yield key, type(self)(df, key_names=kn)
            else:
                yield key, self.df2value(df, last_only)

    def __iter__(self, process: bool=True) -> Iterable:
        return self.iter(self.key_names, process=process)

    def keys(self, columns: Optional[list[str]]=None) -> list:
        return [ keys for keys, _ in self.iter(columns=columns, process=True) ]

    def values(self, process: bool=True) -> list:
        return [ value for _, value in self ]
        
    def save(self, directory: Union[str, Path]) -> tuple[str, str]:
        assert self.meta.name is not None, f"{type(self).__name__} has no save filename"
        path = Path(directory) / f"{self.meta.name}.csv"
        self.to_csv(path, index=False)
        return type(self).__name__, str(path)

    def __repr__(self) -> str:
        return f"key_names={self.key_names}\nvalue_names={self.value_names}\n\n{DataFrame(self)}"
