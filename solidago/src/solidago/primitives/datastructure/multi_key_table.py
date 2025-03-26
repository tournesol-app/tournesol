from typing import Union, Optional, Callable, Any, Iterable
from pathlib import Path
from pandas import DataFrame, Series

import pandas as pd
import math

from solidago.primitives.datastructure.nested_dict import NestedDict


class MultiKeyTable:
    name: str="multi_key_table"
    value_factory: Callable=lambda: None
    value_cls: type=object
    
    def __init__(self, 
        keynames: Union[str, list[str]], 
        init_data: Optional[Union[NestedDict, Any]]=None,
        parent_tuple: Optional[tuple["MultiKeyTable", tuple, tuple]]=None,
        *args, **kwargs
    ):
        """ This class aims to facilitate the use of multi-key tables, like pandas DataFrame.
        In particular, it heavily leverages caching to accelerate access,
        while enabling a decomposition into child tables filtered by one key.
        In particular, modifications to child tables update the parent tables.
        From a mathematical point of view, the class implements a sparse tensor.
        """
        # self.keynames defines the default caching
        self.keynames = (keynames,) if isinstance(keynames, str) else tuple(keynames)
        self._cache = dict() # No cache at initialization for fast instantation
        self.init_data = init_data
        if isinstance(init_data, MultiKeyTable):
            assert self.depth == init_data.depth
            self._cache = init_data._cache
            for keynames, nested_dict in self._cache.items():
                nested_dict.value_factory = type(self).value_factory
            self.init_data = None
        elif isinstance(init_data, NestedDict): # Can be directly plugged in
            assert self.depth == init_data.depth
            init_data.value_factory = type(self).value_factory
            self._cache[self.keynames] = init_data
            self.init_data = None
        elif isinstance(init_data, dict) and init_data:
            def valid(keys, value):
                return len(keys) == self.depth and isinstance(value, NestedDict) and \
                    value.depth == self.depth and value.value_factory() == type(self).value_factory()
            if all({ valid(keys, value) for keys, value in init_data.items() }):
                self._cache = init_data
                self.init_data = None
                if self.keynames not in self._cache:
                    self.init_data = next(iter(self._cache.items()))
        self.parent, self.parent_keynames, self.parent_keys = parent_tuple or (None, None, None)
    
    @property
    def depth(self) -> int:
        return len(self.keynames)
    
    @property
    def parent_tuple(self) -> tuple["MultiKeyTable", tuple, tuple]:
        return self.parent, self.parent_keynames, self.parent_keys
    
    """ The following methods could be worth redefining in derived classes """
    def value2series(self, value: "Value") -> Series:
        return Series(dict(value=value))
    
    def series2value(self, previous_value: Any, row: Series) -> "Value":
        """ previous_value may be used, e.g. if it a list, and we want to append row """
        return row["value"]

    """ The following methods are are more standard """
    def _main_cache(self) -> NestedDict:
        """ This method is complicated because it handles multiple structures of self.init_data 
        to construct a first main cache that corresponds to self.keynames
        """
        if self.keynames in self._cache:
            return self._cache[self.keynames]
        if self._cache:
            keynames, d = next(iter(self._cache.items()))
            assert set(keynames) == set(self.keynames), (keynames, self.keynames)
            self._cache[self.keynames] = NestedDict(type(self).value_factory, self.depth)
            for d_keys, value in d:
                kwargs = { kn: d_keys[kn] for kn in keynames }
                keys = tuple(kwargs[kn] for kn in self.keynames)
                self._cache[self.keynames][*keys] = value
        self._cache[self.keynames] = NestedDict(type(self).value_factory, self.depth)
        if self.init_data is None:
            return self._cache[self.keynames]
        if isinstance(self.init_data, DataFrame):
            for _, row in self.init_data.iterrows():
                keys = tuple(row[kn] for kn in self.keynames)
                value = self._cache[self.keynames][keys]
                self._cache[self.keynames][keys] = self.series2value(value, row)
            return self._cache[self.keynames]
        kns_and_nd = isinstance(self.init_data, tuple) and len(self.init_data) == 2 
        kns_and_nd = kns_and_nd and isinstance(self.init_data[0], tuple)
        kns_and_nd = kns_and_nd and isinstance(self.init_data[1], NestedDict)
        if kns_and_nd:
            keynames, nested_dict = self.init_data
            for keys, value in nested_dict:
                kwargs = dict(zip(keynames, keys))
                new_keys = tuple(kwargs[kn] for kn in self.keynames)
                self._cache[self.keynames][new_keys] = value
        if isinstance(self.init_data, list):
            for entry in self.init_data:
                assert len(entry) == self.depth + 1
                if isinstance(entry, (tuple, list)):
                    keys, value = tuple(entry[:-1]), entry[-1]
                elif isinstance(entry, dict):
                    assert len(entry) == self.depth + 1
                    keys, value = tuple(entry[kn] for kn in self.keynames), entry["value"]
                self._cache[self.keynames][keys] = value
            return self._cache[self.keynames]
        if isinstance(self.init_data, dict):
            for keys, value in self.init_data.items():
                self._cache[self.keynames][keys] = value
            return self._cache[self.keynames]
        raise ValueError(f"Type {type(self.init_data)} of raw data {self.init_data} not handled")

    def cache(self, *keynames) -> None:
        """ Caches but does not return the cached nested dict """
        self.nested_dict(*keynames)

    def nested_dict(self, *keynames) -> NestedDict:
        """ Caches and returns the cached nested dict """
        self._main_cache()
        keynames = [keynames] if isinstance(keynames, str) else list(keynames or list())
        keynames = tuple(keynames + [k for k in self.keynames if k not in keynames])
        assert set(keynames) == set(self.keynames)
        if keynames in self._cache:
            return self._cache[keynames]
        self._cache[keynames] = NestedDict(type(self).value_factory, self.depth)
        for keys, value in self._cache[self.keynames]:
            kwargs = dict(zip(self.keynames, keys))
            new_keys = tuple(kwargs[kn] for kn in keynames)
            self._cache[keynames][new_keys] = value
        return self._cache[keynames]
    
    def get_matching_prefix_caches(self, *keynames) -> set[tuple]:
        """ Searches a cache_keynames such that set(keynames) == set(cache_keynames[:len(keynames)])
        If so, returns (cache_keynames, self._cache[cache_keynames])
        Otherwise, adds a new cache entry 
        
        Returns
        -------
        cache_keynames: tuple
            tuple of all keynames, as it appears in NestedDict and in self._cache
        nested_dict: NestedDict
        """
        keynames = (keynames,) if isinstance(keynames, str) else tuple(keynames)
        matching_keynames = set()
        for cache_keynames in self._cache:
            if set(keynames) == set(cache_keynames[:len(keynames)]):
                matching_keynames.add(cache_keynames)
        if matching_keynames:
            return matching_keynames
        keynames = tuple(list(keynames) + [k for k in self.keynames if k not in keynames])
        self.nested_dict(*keynames)
        return {keynames}

    def iter(self, *keynames) -> Iterable:
        keynames = (keynames,) if isinstance(keynames, str) else keynames
        keynames = keynames if keynames else self.keynames
        other_keynames = [kn for kn in self.keynames if kn not in keynames]
        for keys, value in self.nested_dict(*keynames).iter(len(keynames)):
            if len(keynames) == self.depth:
                yield keys, value
            else:
                init_data = dict()
                yield keys, self.get(*keys)
        
    def __iter__(self) -> Iterable:
        return self.iter()
    
    def keys(self, *keynames) -> set:
        f = lambda k: k[0] if len(k) == 1 else k
        return { f(keys) for keys, _ in self.iter(*keynames) }

    def values(self) -> list:
        return [ value for _, value in self ]
        
    def keys2kwargs(self, *args, **kwargs) -> dict:
        """ args is assumed to list keys, though some may be specified through kwargs """
        assert len(args) + len(kwargs) <= self.depth
        f = lambda v: v if isinstance(v, (str, int)) else str(v)
        kwargs = { k: f(v) for k, v in kwargs.items() }
        other_keynames = [ k for k in self.keynames if k not in kwargs ]
        return kwargs | { k: f(v) for k, v in zip(other_keynames, args) }
    
    def get(self, *args, **kwargs) -> Union["MultiKeyTable", "Value"]:
        kwargs = self.keys2kwargs(*args, **kwargs)
        if len(kwargs) == self.depth:
            keys = tuple(kwargs[kn] for kn in self.keynames)
            return self.nested_dict()[keys]
        other_keynames = [kn for kn in self.keynames if kn not in kwargs]
        keynames_set = self.get_matching_prefix_caches(*kwargs.keys())
        to_keys = lambda keynames: [kwargs[kn] for kn in keynames[:len(kwargs)]]
        parent_keynames = next(iter(keynames_set))[:len(kwargs)]
        parent_keys = tuple(kwargs[kn] for kn in parent_keynames)
        return type(self)(other_keynames, {
            keynames[len(kwargs):]: self._cache[keynames][*to_keys(keynames)]
            for keynames in keynames_set
        }, (self, parent_keynames, parent_keys))

    def __getitem__(self, keys: Union[str, tuple, list]) -> Union["MultiKeyTable", "Value"]:
        keys = keys if isinstance(keys, (tuple, list)) else (keys,)
        return self.get(*keys)
            
    def __contains__(self, *args, **kwargs) -> bool:
        kwargs = self.keys2kwargs(*args, **kwargs)
        keynames = next(iter(self.get_matching_prefix_caches(*kwargs.keys())))[:len(kwargs)]
        keys = tuple(kwargs[kn] for kn in keynames[:len(kwargs)])
        return keys in self.nested_dict(*keynames)

    def __len__(self) -> int:
        return len(self._main_cache())
    
    def __bool__(self) -> bool:
        return bool(self._main_cache())

    def __or__(self, other: "MultiKeyTable") -> "MultiKeyTable":
        assert type(self) == type(other) and set(self.keynames) == set(other.keynames)
        init_data = { kns: nd.deepcopy() for kns, nd in self._cache.items() }
        result = type(self)(self.keynames, init_data, self.parent_tuple)
        for keys, value in other:
            kwargs = dict(zip(other.keynames, keys))
            result[tuple(kwargs[kn] for kn in self.keynames)] = value
        return result
        
    def __ior__(self, other: "MultiKeyTable") -> None:
        assert set(self.keynames) == set(other.keynames)
        for keys, value in other:
            kwargs = dict(zip(other.keynames, keys))
            new_keys = tuple(kwargs[kn] for kn in self.keynames)
            self[new_keys] = value
        
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
        assert isinstance(value, object)
        kwargs = self.keys2kwargs(*args, **kwargs)
        self._main_cache()
        for keynames in self._cache:
            keys = tuple(kwargs[kn] for kn in keynames)
            self._cache[keynames][keys] = value
        if self.parent: # Required because child may have created a cache absent from parent
            kwargs = kwargs | dict(zip(self.parent_keynames, self.parent_keys))
            self.parent.set(value, **kwargs)
    
    def __setitem__(self, keys: Union[str, tuple, list], value: "Value") -> None:
        keys = keys if isinstance(keys, (tuple, list)) else (keys,)
        self.set(*keys, value)

    def delete(self, *args, tolerate_key_error: bool=False, **kwargs) -> None:
        kwargs = self.keys2kwargs(*args, **kwargs)
        for keynames in self._cache:
            keys = [kwargs[kn] for kn in keynames]
            try:
                del self._cache[keynames][keys]
            except KeyError as e:
                if not tolerate_key_error:
                    raise e
        if self.parent: # Required because parent may have created a cache absent from child
            kwargs = kwargs | dict(zip(self.parent_keynames, self.parent_keys))
            self.parent.delete(tolerate_key_error=True, **kwargs)
    
    def __delitem__(self, keys: Union[str, tuple, list]) -> None:
        keys = keys if isinstance(keys, (tuple, list)) else (keys,)
        self.delete(*keys)

    def prepend_keyname(self, keyname: str, key: Union[int, str]) -> "MultiKeyTable":
        assert self.parent is None, "Cannot prepend keyname to MultiKeyTablel with a parent"
        nd = NestedDict(type(self).value_factory, self.depth + 1)
        nd._dict[key] = self._cache
        return type(self)((keyname, *self.keynames), nd)
    
    @classmethod
    def load(cls, directory: str, name: Optional[str]=None, **kwargs) -> "MultiKeyTable":
        if name is None:
            return cls(**kwargs)
        filename = f"{directory}/{name}"
        try:
            return cls(init_data=pd.read_csv(filename, keep_default_na=False), **kwargs)
        except (pd.errors.EmptyDataError, ValueError):
            return cls(**kwargs)
    
    def to_df(self) -> DataFrame:
        return DataFrame([ 
            Series(dict(zip(self.keynames, keys)) | dict(self.value2series(value)))
            for keys, value in self
        ])

    def save(self, directory: Union[str, Path], name: Optional[str]=None) -> tuple[str, dict]:
        if not self:
            return type(self).__name__, dict(keynames=self.keynames)
        name = name or f"{self.name}.csv"
        filename = f"{directory}/{name}"
        self.to_df().to_csv(filename, index=False)
        return type(self).__name__, dict(name=name, keynames=self.keynames)

    def __repr__(self) -> str:
        return f"name={self.name}\nkeynames={self.keynames}\n\n{self.to_df()}"
    
