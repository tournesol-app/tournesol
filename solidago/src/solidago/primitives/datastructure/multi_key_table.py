from typing import Union, Optional, Any, Iterable
from pathlib import Path
from pandas import DataFrame, Series
from collections import defaultdict

import pandas as pd
import csv

from solidago.primitives.datastructure.nested_dict import NestedDict

Value = Any


class MultiKeyTable:
    name: str="multi_key_table"
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
        # self._cache[keynames] is a NestedDict object, where keynames is tuple of str
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
    
    def deepcopy(self) -> "MultiKeyTable":
        copy = type(self)(self.keynames)
        for keys, value in self:
            copy[keys] = value
        return copy
    
    @property
    def depth(self) -> int:
        return len(self.keynames)
    
    @property
    def parent_tuple(self) -> tuple["MultiKeyTable", tuple, tuple]:
        return self.parent, self.parent_keynames, self.parent_keys
    
    """ The following methods could be worth redefining in derived classes """
    @classmethod
    def value_factory(cls):
        return None
    
    @property
    def valuenames(self) -> tuple:
        return ("value",)
    
    def value2tuple(self, value: "Value") -> tuple:
        return (value,)
            
    def series2value(self, previous_value: Any, row: Series) -> "Value":
        """ previous_value may be used, e.g. if it a list, and we want to append row """
        values = tuple(row[name] for name in self.valuenames)
        return values[0] if len(values) == 1 else values

    """ The following methods are are more standard """
    def value2series(self, value: "Value") -> Series:
        return Series(dict(zip(self.valuenames, self.value2tuple(value))))
        
    def _init_data_to_dict(self) -> dict:
        if self.init_data is None and not self._cache:
            return dict()
        if self._cache:
            keynames, d = next(iter(self._cache.items()))
            return { self.keys2tuple(**dict(zip(keynames, keys))): value for keys, value in d }
        if isinstance(self.init_data, DataFrame):
            d = defaultdict(lambda: None)
            for _, row in self.init_data.iterrows():
                keys = tuple(row[kn] for kn in self.keynames)
                d[keys] = self.series2value(d[keys], row)
            return d
        kns_and_nd = isinstance(self.init_data, tuple) and len(self.init_data) == 2 
        kns_and_nd = kns_and_nd and isinstance(self.init_data[0], tuple)
        kns_and_nd = kns_and_nd and isinstance(self.init_data[1], NestedDict)
        if kns_and_nd:
            keynames, nested_dict = self.init_data
            return { self.keys2tuple(**dict(zip(k, keynames))): v for k, v in nested_dict }
        if isinstance(self.init_data, list):
            d = dict()
            for entry in self.init_data:
                assert len(entry) == self.depth + 1
                if isinstance(entry, (tuple, list)):
                    d[tuple(entry[:-1])] = entry[-1]
                elif isinstance(entry, dict):
                    assert len(entry) == self.depth + 1
                    d[tuple(entry[kn] for kn in self.keynames)] = entry["value"]
            return d
        if isinstance(self.init_data, dict):
            return self.init_data
        raise ValueError(f"Type {type(self.init_data)} of raw init_data {self.init_data} not handled")
    
    def _main_cache(self) -> NestedDict:
        """ This method is complicated because it handles multiple structures of self.init_data 
        to construct a first main cache that corresponds to self.keynames
        """
        if self.keynames in self._cache:
            return self._cache[self.keynames]
        d = self._init_data_to_dict()
        self._cache[self.keynames] = NestedDict(type(self).value_factory, self.depth)
        for keys, value in d.items():
            self._cache[self.keynames][keys] = value
        return self._cache[self.keynames]

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
    
    def get_matching_prefix_caches(self, *keynames_sets) -> set[tuple]:
        """ Searches a cache_keynames such that 
        keynames_sets[0] == set(cache_keynames[:len(keynames_sets[0])])
        keynames_sets[0] | keynames_sets[1] == set(cache_keynames[:len(keynames_sets[0])+len(keynames_sets[1])]),
        and so on.
        If so, returns (cache_keynames, self._cache[cache_keynames])
        Otherwise, adds a new cache entry 
        
        Returns
        -------
        cache_keynames: tuple
            tuple of all keynames, as it appears in NestedDict and in self._cache
        nested_dict: NestedDict
        """
        keynames_sets = [{kn_set} if isinstance(kn_set, str) else set(kn_set) for kn_set in keynames_sets]
        matching_keynames = set()
        for cache_keynames in self._cache:
            matches, keynames = True, set()
            for keynames_set in keynames_sets:
                keynames |= keynames_set
                if keynames != set(cache_keynames[:len(keynames)]):
                    matches = False
                    break
            if matches:
                matching_keynames.add(cache_keynames)
        if matching_keynames:
            return matching_keynames
        keynames = sum([list(keynames_set) for keynames_set in keynames_sets], list())
        keynames += [kn for kn in self.keynames if kn not in keynames]
        self.nested_dict(*keynames)
        return {tuple(keynames)}

    def iter(self, *keynames) -> Iterable:
        keynames = (keynames,) if isinstance(keynames, str) else keynames
        keynames = keynames if keynames else self.keynames
        other_keynames = [kn for kn in self.keynames if kn not in keynames]
        assert len(keynames) + len(other_keynames) == self.depth, (keynames, self.keynames)
        for keys, value in self.nested_dict(*keynames).iter(len(keynames)):
            if len(keynames) == self.depth:
                yield keys, value
            else:
                init_data = dict()
                yield keys, self.get(**dict(zip(keynames, keys)))
        
    def __iter__(self) -> Iterable:
        return self.iter()
    
    def keys(self, *keynames) -> set:
        f = lambda k: k[0] if len(k) == 1 else k
        return { f(keys) for keys, _ in self.iter(*keynames) }

    def values(self) -> list:
        return [ value for _, value in self ]

    def convert_key(key) -> Union[int, str, set]:
        from solidago.primitives.datastructure.objects import Objects
        if isinstance(key, Objects):
            return {o.name for o in key}
        return key if isinstance(key, (str, int, set)) else key.name

    def keys2kwargs(self, *args, **kwargs) -> dict:
        """ args is assumed to list keys, though some may be specified through kwargs """
        assert len(args) + len(kwargs) <= self.depth
        assert all({keyname in self.keynames for keyname in kwargs})
        f = MultiKeyTable.convert_key
        kwargs = { kn: f(key) for kn, key in kwargs.items() if key is not all }
        other_keynames = [ k for k in self.keynames if k not in kwargs ]
        return kwargs | { kn: f(key) for kn, key in zip(other_keynames, args) if key is not all }
    
    def keys2tuple(self, *args, keynames: Optional[tuple]=None, **kwargs) -> tuple:
        keynames = keynames or self.keynames
        kwargs = self.keys2kwargs(*args, **kwargs)
        return tuple(kwargs[kn] for kn in keynames)
    
    def get(self, *args, **kwargs) -> Union["MultiKeyTable", "Value"]:
        kwargs = self.keys2kwargs(*args, **kwargs)
        set_keynames = {kn for kn in kwargs if isinstance(kwargs[kn], set)}
        if set_keynames:
            nonset_keynames = {kn for kn in kwargs if not isinstance(kwargs[kn], set)}
            matching_keynames = self.get_matching_prefix_caches(nonset_keynames, set_keynames)
            parent_keynames = next(iter(matching_keynames))[:len(nonset_keynames)]
            parent_keys = tuple(kwargs[kn] for kn in parent_keynames)
            other_keynames = [kn for kn in self.keynames if kn not in kwargs]
            to_keys = lambda keynames: tuple(kwargs[kn] for kn in keynames[:len(kwargs)])
            return type(self)(next(iter(matching_keynames))[len(nonset_keynames):], {
                keynames[len(nonset_keynames):]: self._cache[keynames][to_keys(keynames)]
                for keynames in matching_keynames
            }, (self, parent_keynames, parent_keys))
        if len(kwargs) == self.depth:
            keys = tuple(kwargs[kn] for kn in self.keynames)
            return self.nested_dict()[keys]
        other_keynames = [kn for kn in self.keynames if kn not in kwargs]
        keynames_set = self.get_matching_prefix_caches(kwargs.keys())
        parent_keynames = next(iter(keynames_set))[:len(kwargs)]
        parent_keys = tuple(kwargs[kn] for kn in parent_keynames)
        to_keys = lambda keynames: tuple(kwargs[kn] for kn in keynames[:len(kwargs)])
        return type(self)(other_keynames, {
            keynames[len(kwargs):]: self._cache[keynames][to_keys(keynames)]
            for keynames in keynames_set
        }, (self, parent_keynames, parent_keys))
    
    def __getitem__(self, keys: Union[str, tuple, list, set]) -> Union["MultiKeyTable", "Value"]:
        keys = keys if isinstance(keys, (tuple, list)) else (keys,)
        return self.get(*keys)
            
    def __contains__(self, *args, **kwargs) -> bool:
        kwargs = self.keys2kwargs(*args, **kwargs)
        keynames = next(iter(self.get_matching_prefix_caches(set(kwargs.keys()))))[:len(kwargs)]
        keys = tuple(kwargs[kn] for kn in keynames[:len(kwargs)])
        return keys in self.nested_dict(*keynames)

    def __len__(self) -> int:
        if self.keynames in self._cache:
            return len(self.nested_dict())
        elif self._cache:
            nested_dict = next(iter(self._cache.values()))
            return len(nested_dict)
        try:
            return len(self.init_data)
        except TypeError:
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
        
    def __ior__(self, other: "MultiKeyTable") -> "MultiKeyTable":
        assert set(self.keynames) == set(other.keynames)
        for keys, value in other:
            kwargs = dict(zip(other.keynames, keys))
            new_keys = tuple(kwargs[kn] for kn in self.keynames)
            self[new_keys] = value
        return self
        
    def set(self, *args, **kwargs) -> None:
        """ args is assumed to list keys and then value, 
        though some may be specified through kwargs """
        assert len(args) + len(kwargs) == self.depth + 1
        if "value" in kwargs:
            value = kwargs["value"]
            del kwargs["value"]
        else:
            args, value = args[:-1], args[-1]
        assert isinstance(value, type(self).value_cls)
        kwargs = self.keys2kwargs(*args, **kwargs)
        assert all({isinstance(v, (str, int)) for v in kwargs.values()})
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
        nonset_keynames = {kn for kn in kwargs if not isinstance(kwargs[kn], set)}
        if len(nonset_keynames) < self.depth:
            keynames = next(iter(self.get_matching_prefix_caches(nonset_keynames)))
            parent_keys = [kwargs[kn] for kn in keynames[:len(nonset_keynames)]]
            def matching_sub_keys(sub_keys):
                for key, keyname in zip(sub_keys, keynames[len(nonset_keynames):]):
                    if keyname in kwargs and key != kwargs[keyname] and key not in kwargs[keyname]:
                        return False
                return True
            sub_nested_dict = self.nested_dict(*keynames)[parent_keys]
            for sub_keys in [sk for sk, _ in sub_nested_dict if matching_sub_keys(sk)]:
                self.delete(**dict(zip(keynames, parent_keys + list(sub_keys))))
            return None
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

    def prepend(self, **kwargs) -> "MultiKeyTable":
        assert self.parent is None, "Cannot prepend keyname to MultiKeyTablel with a parent"
        prekeynames, prekeys = tuple(kwargs.keys()), tuple(kwargs.values())
        keynames = (*prekeynames, *self.keynames)
        result = type(self)(keynames)
        result._cache[keynames] = NestedDict(type(self).value_factory, self.depth + len(kwargs))
        subdict = result._cache[keynames]._dict
        for key in prekeys[:-1]:
            subdict[key] = dict()
            subdict = subdict[key]
        subdict[prekeys[-1]] = self.nested_dict()._dict
        return result

    def reorder(self, *keynames) -> "MultiKeyTable":
        self._main_cache()
        keynames = list(keynames) + [kn for kn in self.keynames if kn not in keynames]
        assert len(keynames) == self.depth
        return type(self)(keynames, self._cache)
    
    def detach(self) -> "MultiKeyTable":
        """ Removes reference to parent """
        return type(self)(self.keynames, self._cache)
    
    @classmethod
    def load(cls, directory: str, name: Optional[str]=None, **kwargs) -> "MultiKeyTable":
        if name is None:
            return cls(**kwargs)
        filename = f"{directory}/{name}"
        try:
            return cls(init_data=pd.read_csv(filename, keep_default_na=False), **kwargs)
        except (pd.errors.EmptyDataError, ValueError):
            return cls(**kwargs)
    
    def to_df(self, max_values: Union[int, float]=float("inf")) -> DataFrame:
        df_list = list()
        for index, (keys, value) in enumerate(self):
            if index >= max_values:
                break
            df_list.append(Series(dict(zip(self.keynames, keys)) | dict(self.value2series(value))))
        return DataFrame(df_list)

    def df_save(self, directory: Union[str, Path], name: Optional[str]=None) -> tuple[str, dict]:
        name = name or f"{self.name}.csv"
        if not directory:
            return self.save_instructions(name)
        filename = f"{directory}/{name}"
        self.to_df().to_csv(filename, index=False)
        return self.save_instructions(name)
    
    def save(self, directory: Union[str, Path], name: Optional[str]=None) -> tuple[str, dict]:
        name = name or f"{self.name}.csv"
        if not directory:
            return self.save_instructions(name)
        filename = f"{directory}/{name}"
        with open(filename, 'w', newline='') as f:
            w = csv.writer(f, delimiter=',')
            w.writerow(list(self.keynames) + list(self.valuenames))
            for keys, value in self:
                w.writerow(list(keys) + list(self.value2tuple(value)))
        return self.save_instructions(name)
    
    def save_instructions(self, name: Optional[str]=None) -> tuple[str, dict]:
        name = name or f"{self.name}.csv"
        return dict(classname=type(self).__name__, name=name, keynames=self.keynames)

    def __repr__(self) -> str:
        r = f"name={self.name}\nkeynames={self.keynames}\n\n{self.to_df(5)}"
        return r + (f"\n\n... ({len(self)} items)" if len(self) > 5 else "")
        
    
