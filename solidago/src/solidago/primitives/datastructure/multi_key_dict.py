from typing import Union, Optional, Callable, Any, Iterable
from types import BuiltinFunctionType, SimpleNamespace
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce
from collections import defaultdict

import pandas as pd
import math
import numbers

from solidago.primitives.datastructure.nested_dict import NestedDict


class MultiKeyTable:
    name: str="multi_key_table"
    value_factory: Callable=lambda: None
    
    def __init__(self, 
        keynames: Optional[Union[str, list[str]]]=None, 
        init_data: Optional[Union[NestedDict, Any]]=None,
        parent: Optional["MultiKeyTable"]=None,
        parent_keys: Optional[tuple]=None,
        *args,
        **kwargs
    ):
        self.keynames = tuple(keynames) # Defines the default caching
        self._cache = dict() # No cache at initialization for fast instantation
        if isinstance(init_data, NestedDict): # Can be directly plugged in
            assert self.value_factory() == init_data.value_factory()
            assert self.depth == init_data.depth
            self._cache[self.keynames] = init_data
        else:
            self.init_data = init_data
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
    def _main_cache(self) -> NestedDict:
        """ This method is complicated because it handles multiple structures of self.init_data 
        to construct a first main cache that corresponds to self.keynames
        """
        if self.keynames in self._cache:
            return self._cache[self.keynames]
        if self._cache:
            keynames, d = next(iter(self._cache))
            assert set(keynames) == set(self.keynames)
            self._cache[self.keynames] = NestedDict(self.value_factory, self.depth)
            for d_keys, value in d:
                kwargs = { kn: d_keys[kn] for kn in keynames }
                keys = [ kwargs[kn] for kn in self.keynames ]
                self._cache[self.keynames][keys] = value
        self._cache[self.keynames] = NestedDict(self.value_factory, self.depth)
        if isinstance(self.init_data, DataFrame):
            for _, row in self.init_data.iterrows():
                keys = [row[kn] for kn in self.keynames]
                self._cache[self.keynames][keys] = self.series2stored_value(row)
            return self._cache[self.keynames]
        if isinstance(self.init_data, list):
            for entry in self.init_data:
                assert len(entry) == self.depth + 1
                if isinstance(entry, (tuple, list)):
                    keys, value = tuple(entry[:-1]), entry[-1]
                elif isinstance(entry, dict):
                    assert len(entry) == self.depth + 1
                    keys, value = tuple(entry[kn] for kn in self.keynames), entry["value"]
                self._cache[self.keynames][keys] = self.value2stored_value(value)
            return self._cache[self.keynames]
        if isinstance(self.init_data, dict):
            init_data = { k: self.value2stored_value(v) for k, v in self.init_data.items() }
            self._cache[self.keynames].load(init_data)
            return self._cache[self.key_names]
        raise ValueError(f"Type {type(self.init_data)} of raw data {self.init_data} not handled")
    
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
        self._cache
        return self._cache
        
    def __iter__(self, process: bool=True) -> Iterable:
        return self.iter(self.keynames, process)
    
    def keys2kwargs(self, *args, **kwargs) -> dict:
        """ args is assumed to list keys, though some may be specified through kwargs """
        assert len(args) + len(kwargs) <= self.depth
        kwargs = { k: str(v) for k, v in kwargs.items() }
        other_keynames = [ k for k in self.keynames if k not in kwargs ]
        return kwargs | { k: str(v) for k, v in zip(other_keynames, args) }
    
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
        parent_keys = [kwargs[kn] for kn in keynames]
        cache = {
            kns[len(keynames:]): d[tuple(kwargs[kn] for kn in kns[:len(keynames)])]
            for kns, d in self._cache.items()
            if set(kns[:len(keynames)]) == set(keynames)
        }
        return type(self)(other_keynames, value, self, parent_keys, cache)
    
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

    def __or__(self, other: "MultiKeyDict") -> "MultiKeyDict":
        main, other = (self, other) if isinstance(other, type(self)) else (other, self)
        assert isinstance(other, type(main)) and set(main.keynames) == set(other.keynames)
        result = type(main)(main.keynames, None, main.parent, main.parent_keys, main._cache)
        for keys, value in others:
            main_keys = [keys[kn] for kn in main.keynames]
            result[keys] = value
        return result
        
    def set(self, *args, **kwargs) -> None:
        """ args is assumed to list keys and then value, 
        though some may be specified through kwargs """
        assert len(args) + len(kwargs) == self.depth + 1
        if "value" not in kwargs: # args[-1] is value
            value = args[-1]
            args = args[:-1]
        else:
            assert "value" in kwargs
            value = kwargs["value"]
            del kwargs["value"]
        kwargs = self.keys2kwargs(*args, **kwargs)
        keys = [kwargs[kn] for kn in self.keynames]
        
    
    def __setitem__(self, keys: tuple, value: "Value") -> None:
        self.set(*keys, value)


    # Below is TBD

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
        kns = [ kn for kn in self.key_names if kn not in columns ]
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

