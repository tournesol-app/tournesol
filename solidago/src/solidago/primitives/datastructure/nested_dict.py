from abc import ABC, abstractmethod
from typing import Union, Optional, Callable, Any, Iterable
from types import BuiltinFunctionType
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce

import pandas as pd


class NestedDict(ABC):
    def __init__(self, 
        d: Optional[Union["NestedDict", dict, DataFrame]]=None,
        key_names: list[str]=["key"], 
        save_filename: Optional[str]=None,
    ):
        """ Defines a nested dict for sparse data storage of values with multiple keys """
        assert len(key_names) >= 1
        self.key_names = key_names
        self._dict = dict()
        self.save_filename = save_filename
        self.init_dict(d)
        
    def init_dict(self, d: Union["NestedDict", dict, DataFrame]) -> None:
        if isinstance(d, NestedDict):
            self._dict |= d._dict
        elif isinstance(d, dict) and len(self.key_names) == 1:
            self._dict |= d
        elif isinstance(d, dict):
            self._dict |= {
                key: type(self)(d=value, key_names=self.key_names[1:])
                for key, value in d.items()
            }
        elif isinstance(d, DataFrame):
            for _, row in d.iterrows():
                self.add_row([row[key_name] for key_name in self.key_names], row)
    
    """ The following are classes that could be worth redefining in derived classes """
    def default_value(self) -> Any:
        return None
    
    def process_stored_value(self, keys: list[str], stored_value: Any) -> Any:
        return stored_value
    
    def sanitize(self, injected_value: Any) -> Any:
        return injected_value
    
    @abstractmethod
    def add_row(self, keys: list[str], row: Union[dict, Series]) -> None:
        raise NotImplemented
        
    def get(self, *keys, process: bool=False) -> Union["NestedDict", Any]:
        assert len(keys) <= len(self.key_names), (keys, repr(self))
        out_key_names = [ 
            key_name for key_name, key in zip(self.key_names[:len(keys)], keys)
            if (isinstance(key, BuiltinFunctionType) and key == any) or isinstance(key, (set, tuple, list))
        ] + self.key_names[len(keys):]
        if len(keys) == 0:
            return self
        if _is_any(keys[0]) and len(keys) == 1:
            return self
        if _is_any(keys[0]) or isinstance(keys[0], (set, tuple, list)): # len(keys) > 1
            result = type(self)(key_names=out_key_names, save_filename=None)
            valid_key = lambda key: True if _is_any(keys[0]) else key in keys[0]
            d = { key: subdict.get(*keys[1:]) for key, subdict in self._dict.items() if valid_key(key) }
            result._dict = { key: subdict for key, subdict in d.items() if len(subdict) > 0  }
            return result
        if str(keys[0]) not in self._dict and len(out_key_names) == 0:
            return self.default_value()
        elif str(keys[0]) not in self._dict: # and len(out_key_names) > 0
            return type(self)(key_names=out_key_names, save_filename=None)
        if len(keys) == 1:
            value = self._dict[str(keys[0])]
            if process and len(self.key_names) == 1:
                return self.process_stored_value(keys, value)
            return value
        return self._dict[str(keys[0])].get(*keys[1:], process=process)

    def __getitem__(self, keys: Union[str, tuple, list, dict]) -> Union["NestedDict", Any]:
        """ __getitem___ postprocesses the result to make it readily usable for external use """
        if isinstance(keys, dict):
            keys = [(keys[key_name] if key_name in keys else any) for key_name in self.key_names]
        if _is_any(keys):
            return self
        elif isinstance(keys, (tuple, list)):
            return self.get(*keys, process=True)
        return self.get(keys, process=True) # keys is a key

    def __contains__(self, keys: Union[str, tuple, list, dict]) -> bool:
        if isinstance(keys, str):
            return keys in self._dict
        elif isinstance(keys, dict):
            if self.key_names[0] in keys:
                key = keys[self.key_names[0]]
                del keys[self.key_names[0]]
                return keys in self[key]
            if any({ key_name in self.key_names for key_name in keys }):
                return any({ keys in subdict for _, subdict in self._dict.items() })
            return True
        elif len(keys) == 1:
            return str(keys[0]) in self._dict
        assert len(keys) <= len(self.key_names), (keys, self.key_names, self)
        if str(keys[0]) not in self._dict:
            return False
        return keys[1:] in self._dict[str(keys[0])]

    def __or__(self, other: "NestedDict") -> "NestedDict":
        """ If a conflict arises, other takes over """
        assert self.key_names == other.key_names
        result = type(self)(self, key_names=self.key_names)
        for keys, value in other:
            result[keys] = value
        return result
    
    def get_set(self, key_name: str, default_value: Optional[str]=None) -> set:
        if key_name not in self.key_names:
            raise NestedKeyError(key_name)
        if key_name == self.key_names[0]:
            return set(self._dict)
        add_subdict_set = lambda s, subdict: subdict.get_set(key_name) | s
        return reduce(add_subdict_set, self._dict.values(), set())
    
    def set(self, keys: Union[str, tuple, list], value: Union["NestedDict", "OutputValue"], sanitize: bool=False) -> None:
        if isinstance(keys, str):
            keys = [keys]
        if len(keys) == 1:
            if len(self.key_names) == 1:
                self._dict[str(keys[0])] = self.sanitize(value) if sanitize else value
                return None
            assert isinstance(value, type(self)) and value.key_names == self.key_names[1:], (keys, value, self.key_names)
            self._dict[str(keys[0])] = value
            return None
        assert len(keys) <= len(self.key_names), (keys, self.key_names)
        assert len(keys) == len(self.key_names) or isinstance(value, NestedDict), (keys, self.key_names)
        if str(keys[0]) not in self._dict:
            self._dict[str(keys[0])] = type(self)(key_names=self.key_names[1:])
        self._dict[str(keys[0])].set(keys[1:], value, sanitize)

    def __setitem__(self, keys: Union[str, tuple, list], value: Union["NestedDict", "OutputValue"]) -> None:
        self.set(keys, value, sanitize=True)

    def reorder_keys(self, key_names: list[str]) -> "NestedDict":
        if not key_names or self.key_names == key_names:
            return self
        assert all({ key_name in key_names for key_name in self.key_names }), (key_names, self.key_names)
        key_names += [ key_name for key_name in self.key_names if key_name not in key_names ]
        new2self_index = { i: self.key_names.index(key_names[i]) for i in range(len(key_names)) }
        result = type(self)(key_names=key_names)
        for self_keys, value in self.__iter__(value_process=False, key_process=False):
            result[ [self_keys[new2self_index[i]] for i in range(len(key_names))] ] = value
        return result

    @classmethod
    def load(cls, filename: str) -> "NestedDict":
        try: return cls(pd.read_csv(filename, keep_default_na=False))
        except pd.errors.EmptyDataError: return cls()

    def __iter__(self, value_process: bool=True, key_process: bool=True) -> Iterable:
        if len(self.key_names) == 1:
            for key, value in self._dict.items():
                yield (
                    key if key_process else [key], 
                    self.process_stored_value([key], value) if value_process else value
                )
        else:
            for key in self._dict:
                for subkeys, value in self._dict[key].__iter__(value_process=value_process, key_process=False):
                    yield [key] + subkeys, value

    def keys(self, key_process: bool=True) -> list:
        return [ keys for keys, _ in self.__iter__(key_process=key_process) ]

    def values(self, value_process: bool=True) -> list:
        return [ value for _, value in self.__iter__(value_process=value_process) ]
    
    def __len__(self) -> int:
        if len(self.key_names) == 1:
            return len(self._dict)
        return sum([ len(sub_dicts) for sub_dicts in self._dict.values() ])
    
    def to_dict(self, keys: Union[list, tuple], value: Any) -> dict:
        return dict(zip(self.key_names, keys)) | self.value2dict(value)

    @abstractmethod
    def to_rows(self, row_kwargs: Optional[dict]=None) -> list[dict]:
        raise NotImplemented
            
    def to_df(self, row_kwargs: Optional[dict]=None) -> DataFrame:
        return DataFrame(self.to_rows(row_kwargs))

    def save(self, directory: Union[str, Path]) -> tuple[str, str]:
        assert self.save_filename is not None, f"{type(self).__name__} has no save filename"
        path = Path(directory) / self.save_filename
        self.to_df().to_csv(path, index=False)
        return type(self).__name__, str(path)

    def __repr__(self) -> str:
        return repr(self.to_df()) 

def _is_any(key):
    return isinstance(key, BuiltinFunctionType) and key == any


class NestedKeyError(KeyError):
    def __init__(self, message: str):
        super().__init__(message)
