from typing import Union, Optional, Callable, Any, Iterable
from types import BuiltinFunctionType, SimpleNamespace
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce
from collections import defaultdict

import pandas as pd
import math
import numbers


def nested_dict(default_factory: Callable, depth: int) -> defaultdict:
    if depth == 1:
        return defaultdict(default_factory)
    assert isinstance(depth, int) and depth > 1
    return defaultdict(lambda: nested_dict(default_factory, depth - 1))
    
def get_nested_dict_depth(d: defaultdict) -> int:
    assert isinstance(d, defaultdict)
    subdict = d.default_factory()
    return (get_nested_dict_depth(subdict) + 1) if isinstance(subdict, defaultdict) else 1


class MultiKeyDict:
    name: str="multi_key_dict"
    default_factory: Callable=lambda: None
    
    def __init__(self, 
        keynames: Optional[Union[str, list[str]]]=None, 
        raw_data: Optional[dict[tuple, Any]]=None,
        parent: Optional["MultiKeyDict"]=None,
        parent_keys: Optional[tuple]=None,
        cache: Optional[dict]=None
        *args,
        **kwargs
    ):
        self.keynames = tuple(keynames)
        self.raw_data = raw_data # Only used for initialization before caching
        self._cache = cache or dict() # No cache at initialization for fast instantation
        if not cache and isinstance(raw_data, default_dict) and get_nested_dict_depth(raw_data) == self.keynames:
            self.default_factory = raw_data.default_factory
            self._cache[self.keynames] = raw_data
        self.parent = parent
        self.parent_keys = parent_keys
        
    @property
    def depth(self) -> int:
        return len(self.keynames)
        
    """ The following methods could be worth redefining in derived classes """
    def stored_value2value(self, stored_value: "StoredValue") -> "Value":
        return value
    
    def value2stored_value(self, value: "Value") -> "StoredValue":
        return value

    def series2stored_value(self, row: Series) -> "StoredValue":
        return dict(row)

    """ The following methods are are more standard """
    def _first_cache(self) -> defaultdict:
        if self.keynames in self._cache:
            return self._cache[self.keynames]
        self._cache[self.keynames] = self.defaultdict()
        if isinstance(self.raw_data, DataFrame):
            for _, row in self.raw_data.iterrows():
                keys = [row[keyname] for keyname in self.keynames]
                subdict = self._cache[self.keynames]
                for key in keys[:-1]:
                    subdict = subdict[key]
                subdict[keys[-1]] = self.series2stored_value(row)
            return self._cache[self.keynames]
        if isinstance(self.raw_data, list):
            self.raw_data = dict(self.raw_data)
        if isinstance(self.raw_data, dict):
            if not self.raw_data:
                return self._cache[self.key_names]
            first_key = next(iter(self.raw_data))
            if isinstance(first_key, tuple) and len(first_key) == self.depth:
                subdict = self._cache[self.keynames]
                for keys, value in self.raw_data.items():
                    for key in keys[:-1]:
                        subdict = subdict[key]
                    subdict[keys[-1]] = self.value2stored_value(value)
                return self._cache[self.keynames]
            def set_subdicts(input_dict, output_defaultdict, depth):
                for key, subdict in d.items():
                    if depth == 1:
                        output_defaultdict[key] = self.value2stored_value(subdict)
                    else:
                        set_subdicts(subdict, output_defaultdict[key], depth - 1)
            set_subdicts(self.raw_data, self._cache[self.keynames], self.depth)
            return self._cache[self.key_names]
        raise ValueError(f"Type {type(self.raw_data)} of raw data {self.raw_data} not handled")
    
    def __iter__(self, process: bool=True) -> Iterable:
        return self.iter(self.keynames, process)
    
    def iter(self, keynames: Union[str, Iterable], process: bool=True) -> Iterable:
        returns_values = (len(keynames) == self.depth)
        other_keynames = [k for k in self.keynames if k not in keynames]
        def iter_defaultdict(d, depth, prekeys):
            if depth == 1:
                for key, value in d.items():
                    keys = tuple(prekeys + [key])
                    if (len(keynames) == self.depth):
                        v = self.stored_value2value(value) if process else value
                    else:
                        v = type(self)(other_keynames, value, self, tuple(prekeys + [key]))
                    yield keys, v
            else:
                for key, subdict in d.items():
                    yield iter_defaultdict(subdict, depth - 1, prekeys + [key], other_keynames)
        return iter_defaultdict(self.cache(keynames), len(keynames), list())

    def keys2kwargs(self, *args, **kwargs) -> dict:
        """ args is assumed to list keys, though some may be specified through kwargs """
        kwargs = { k: str(v) for k, v in kwargs.items() }
        other_keynames = [ k for k in self.keynames if k not in kwargs ]
        return kwargs | { k: str(v) for k, v in zip(other_keynames, args) }

    def defaultdict(self) -> defaultdict:
        def nested_dict(depth):
            if depth == 1:
                return defaultdict(self.default_value)
            assert isinstance(depth, int) and depth > 1
            return defaultdict(lambda: nested_dict(depth - 1))
        return nested_dict(len(self.keynames))
            
    def cache(self, keynames: Union[str, Iterable]) -> defaultdict:
        keynames = (keynames,) if isinstance(keynames, str) else list(keynames)
        keynames = tuple(keynames + [k for k in self.keynames if k not in keynames])
        if keynames in self._cache:
            return self._cache[keynames]
        if keynames == self.keynames:
            return self._first_cache()
        def nested_dict(depth):
            if depth == 1:
                return defaultdict(self.default_value)
            assert isinstance(depth, int) and depth > 1
            return defaultdict(lambda: nested_dict(depth - 1))
        d = self.defaultdict()
        for keys, value in self.__iter__(process=False):
            subdict = d
            for index, key in enumerate(keys):
                if index == len(keys) - 1:
                    subdict[key] = value
                else:
                    subdict = subdict[key]
        return d
    
    def get(self, *args, process: bool=True, **kwargs) -> Union["MultiKeyDict", "StoredValue", "Value"]:
        kwargs = self.keys2kwargs(*args, **kwargs)
        keynames = [k for k in self.keynames if k in kwargs]
        other_keynames = tuple(k for k in self.keynames if k not in keynames)
        value = self.cache(keynames)
        for keyname in keynames:
            value = value[kwargs[keyname]]
        if not other_keynames: # value is a stored value
            return self.process_stored_value(value) if process else value
        # value is a nested_dict, which we wrap
        return type(self)(other_keynames, value, self, [kwargs[n] for n in keynames])
    
    def __getitem__(self, keys: tuple) -> Union["MultiKeyDict", "StoredValue", "Value"]:
        return self.get(*keys)
            
    def __contains__(self, *args, **kwargs) -> bool:
        kwargs = self.keys2kwargs(*args, **kwargs)
        keynames = [k for k in self.keynames if k in kwargs]
        value = self.cache(keynames)
        for keyname in keynames:
            key = kwargs[keyname]
            if key not in value:
                return False
            value = value[key]
        return True


    # Below is TBD

    def __or__(self, other: "MultiKeyDict") -> "MultiKeyDict":
        main, other = (self, other) if isinstance(other, type(self)) else (other, self)
        assert isinstance(other, type(main)) and set(main.keynames) == set(other.keynames)
        result = type(main)(main.keynames, main.raw_data, main.parent, main.parent_keys)
            data = other
        elif other.empty:
            data = self
        else:
            data = pd.concat([self, other])
            data.index = range(len(data))
        return type(self)(
            data=data, 
            key_names=self.key_names, 
            name=self.meta.name,
            default_value=self.meta._default_value,
            last_only=self.meta._last_only,
        )

    def delete(self, *args, **kwargs) -> "UnnamedDataFrame":
        kwargs = self.input2dict(*args, keys_only=True, **kwargs)
        indices = self.get(process=False, last_only=False, cache_groups=False, **kwargs)
        self_with_deletion = type(self)(
            data=self.drop(indices), 
            key_names=self.key_names,
            name=self.meta.name,
            default_value=self.meta._default_value,
            last_only=self.meta._last_only,
        )
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
    def load(cls, directory: Union[str, Path], *args, **kwargs) -> "UnnamedDataFrame":
        if args and not isinstance(args[0], str):
            return cls(*args, **kwargs)
        filename = f"{directory}/{args[0]}"
        try:
            return cls(pd.read_csv(filename, keep_default_na=False), *args[1:], **kwargs)
        except (pd.errors.EmptyDataError, ValueError):
            return cls(*args[1:], **kwargs)

    def last_only(self) -> "UnnamedDataFrame":
        return type(self)(
            data=DataFrame([ df.iloc[-1] for _, df in self.iter(process=False, last_only=True) ]),
            key_names=self.key_names,
            default_value=self.meta._default_value,
            last_only=True
        )

    def groupby(self, *args, **kwargs) -> "DataFrameGroupBy":
        return DataFrame(self).groupby(*args, **kwargs)

    def to_dict(self, 
        columns: Optional[Union[str, list[str]]]=None, 
        process: bool=True, 
        last_only: Optional[bool]=None,
    ) -> "UnnamedDataFrameDict":
        columns = [columns] if isinstance(columns, str) else columns
        columns = columns if columns else self.key_names
        group_keys = (tuple(columns), process, last_only)
        if group_keys in self.meta._group_cache:
            return self.meta._group_cache[group_keys]
        data = { key: value for key, value in self.iter(columns, process) }
        sub_key_names = [ key for key in self.key_names if key not in columns ]
        if process and not sub_key_names:
            self.meta._group_cache[group_keys] = defaultdict(self.default_value, data)
            return self.meta._group_cache[tuple(columns), process, last_only]
        from solidago.primitives.datastructure import UnnamedDataFrameDict
        self.meta._group_cache[tuple(columns), process, last_only] = UnnamedDataFrameDict(
            data, 
            df_cls=type(self), 
            df_kwargs=dict(
                key_names=sub_key_names,
                name=self.meta.name,
                default_value=self.meta._default_value,
                last_only=self.meta._last_only,
            ),
            main_key_names=columns, 
            sub_key_names=sub_key_names
        )
        return self.meta._group_cache[tuple(columns), process, last_only]
    
    def iter(self, 
        columns: Optional[list[str]]=None, 
        process: bool=True, 
        last_only: Optional[bool]=None
    ) -> Iterable:
        last_only = self.meta._last_only if last_only is None else last_only
        columns = [columns] if isinstance(columns, str) else columns
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
                yield key, type(self)(
                    data=df, 
                    key_names=kn, 
                    name=self.meta.name, 
                    default_value=self.meta._default_value, 
                    last_only=self.meta._last_only
                )
            else:
                yield key, self.df2value(df, last_only)

    def __iter__(self, process: bool=True) -> Iterable:
        return self.iter(self.key_names, process=process)

    def __getitem__(self, *args, **kwargs) -> Series:
        try:
            return super().__getitem__(*args, **kwargs)
        except KeyError:
            return Series()

    def keys(self, columns: Optional[list[str]]=None) -> list:
        return [ keys for keys, _ in self.iter(columns=columns, process=True) ]

    def values(self, process: bool=True) -> list:
        return [ value for _, value in self ]
        
    def save(self, directory: Union[str, Path]) -> tuple[str, str]:
        assert self.meta.name is not None, f"{type(self).__name__} has no save filename"
        if self.empty:
            return type(self).__name__, None
        path = Path(directory) / f"{self.meta.name}.csv"
        self.to_csv(path, index=False)
        return type(self).__name__, f"{self.meta.name}.csv"

    def __repr__(self) -> str:
        return f"name={self.meta.name}\nkey_names={self.key_names}\nvalue_names={self.value_names}" \
            f"\n\n{DataFrame(self)}"

