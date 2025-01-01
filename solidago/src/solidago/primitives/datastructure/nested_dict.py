from typing import Union, Optional, Callable, Any, Iterable
from types import BuiltinFunctionType
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce

import pandas as pd


class NestedDict:
    def __init__(self, 
        d: Optional[Union["NestedDict", dict, DataFrame]]=None,
        key_names: list[str]=["key"], 
        value_names: Optional[list[str]]=None, # if None, then values are lists of dicts
        save_filename: Optional[str]=None,
    ):
        """ Defines a nested dict for sparse data storage of values with multiple keys.
        If value_names is set to None, then values are Series 
        (or they could be a class that inherits Series). """
        assert len(key_names) >= 1
        assert value_names is None or isinstance(value_names, (tuple, list))
        self.key_names = key_names
        self.value_names = value_names
        self._dict = dict()
        self.save_filename = save_filename
        self.init_dict(d)
        
    def init_dict(self, d: Union["NestedDict", dict, DataFrame]) -> None:
        if isinstance(d, NestedDict):
            self._dict |= d._dict
        elif isinstance(d, dict):
            self._dict |= d
        elif isinstance(d, DataFrame):
            for _, row in d.iterrows():
                self.add_row([row[key_name] for key_name in self.key_names], row)
    
    """ The following are classes that could be worth redefining in derived classes """
    def default_value(self) -> Any:
        return None
    
    def process_stored_value(self, keys: list[str], stored_value: Any) -> Any:
        return stored_value
        
    """ The following classes should not be changed """
    def add_row(self, keys: list[str], row: Union[dict, Series]) -> None:
        if self.value_names is None:
            l = self._get(*keys) if keys in self else list()
            self[keys] = l + [dict(row)]
        elif len(self.value_names) == 1:
            self[keys] = self.value_names[0]
        else:
            self[keys] = tuple([row[name] for name in self.value_names])
        
    def _get(self, *keys, default_value: bool=True) -> Union["NestedDict", Any]:
        """ _get does NOT postprocess the result, which makes it usually unsuitable for external use """
        assert len(keys) <= len(self.key_names), (keys, repr(self))
        out_key_names = [ 
            key_name for key_name, key in zip(self.key_names[:len(keys)], keys)
            if (isinstance(key, BuiltinFunctionType) and key == any) or isinstance(key, (set, tuple, list))
        ] + self.key_names[len(keys):]
        if len(keys) == 0:
            return self
        if isinstance(keys[0], BuiltinFunctionType) and keys[0] == any and len(self.key_names) == 1:
            return self
        if isinstance(keys[0], BuiltinFunctionType) and keys[0] == any: # len(self.key_names) > 1 and len(out_key_names) > 0
            d = { key: subdict._get(*keys[1:], default_value=(len(out_key_names) == 0)) for key, subdict in self._dict.items() }
            d = { key: subdict for key, subdict in d.items() if len(subdict) > 0  }
            return type(self)(key_names=out_key_names, value_names=self.value_names, d=d, save_filename=None)
        if isinstance(keys[0], (set, tuple, list)):
            d = { key: subdict._get(*keys[1:], default_value=(len(out_key_names) == 0)) for key, subdict in self._dict.items() if key in keys[0] }
            d = { key: subdict for key, subdict in d.items() if len(subdict) > 0 }
            return type(self)(key_names=out_key_names, value_names=self.value_names, d=d, save_filename=None)
        if str(keys[0]) not in self._dict:
            return self.default_value() if default_value else dict()
        if len(keys) == 1:
            return self._dict[str(keys[0])]
        return self._dict[str(keys[0])]._get(*keys[1:])

    def __getitem__(self, keys: Union[str, tuple, list, dict]) -> Union["NestedDict", Any]:
        """ __getitem___ postprocesses the result to make it readily usable for external use """
        if isinstance(keys, dict):
            keys = [(keys[name] if name in keys else any) for name in self.args_names]
        value = self._get(keys) if keys == any or isinstance(keys, str) else self._get(*keys)
        return value if isinstance(value, NestedDict) else self.process_stored_value(keys, value)

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
        assert self.key_names == other.key_names and self.value_names == other.value_names
        result = type(self)(self._dict, key_names=self.key_names, value_names=self.value_names)
        for keys, value in other:
            result[keys] = value
        return result
    
    def get_set(self, key_name: str, default_value: Optional[str]=None) -> set:
        if key_name == self.key_names[0]:
            return set(self._dict)
        if key_name in self.key_names:
            return reduce(lambda subdict, s: subdict.get_set(key_name) | s, self._dict.values(), set())
        if value_name in self.value_names:
            value_name_index = self.value_names.index(value_name)
            return { values[value_name_index] for _, values in self }
        assert self.value_names is None, f"`{key_name}` must be a key or value name for nonlist values"
        if default_value is None:
            return { 
                row[key_name]
                for _, row_list in self
                for row in row_list if key_name in row
            }
        return {
            row[key_name] if key_name in row else default_value
            for _, row_list in self
            for row in row_list
        }
    
    def set(self, keys: Union[str, tuple, list], value: "OutputValue") -> None:
        if len(keys) == 1:
            assert len(self.key_names) == 1, (keys, self.key_names, self)
            self._dict[str(keys[0])] = value
            return None
        assert len(keys) == len(self.key_names), (keys, self.key_names)
        if str(keys[0]) not in self._dict:
            self._dict[str(keys[0])] = type(self)(key_names=self.key_names[1:], value_names=self.value_names)
        self._dict[str(keys[0])].set(keys[1:], value)

    def add(self, *keys) -> None:
        """ Adds an empty entry to nested_dict[keys] 
        (requires that it be a list of dict, nested_dict.value_names is None """
        assert self.value_names is None, "Cannot add empty entry to NestedDict with nonlist values"
        self[keys] = self._get(*keys) + [dict()]
    
    def append(self, keys: list, row: dict) -> None:
        assert self.value_names is None, "Cannot add dict to NestedDict with nonlist values"
        self[keys] = self._get(*keys) + [dict(row)]

    def __setitem__(self, keys: Union[str, tuple, list], value: "OutputValue") -> None:
        self.set(keys, value)

    @classmethod
    def load(cls, filename: str) -> "NestedDict":
        try: return cls(pd.read_csv(filename, keep_default_na=False))
        except pd.errors.EmptyDataError: return cls()

    def __iter__(self, process: bool=True) -> Iterable:
        if len(self.key_names) == 1:
            for key, value in self._dict.items():
                yield [key], (self.process_stored_value([key], value) if process else value)
        else:
            for key in self._dict:
                for subkeys, value in self._dict[key].__iter__(process=process):
                    yield [key] + subkeys, value
    
    def __len__(self) -> int:
        if len(self.key_names) == 1 and self.value_names is not None:
            return len(self._dict)
        elif len(self.key_names) == 1:
            return sum([len(value) for _, value in self._dict.items()])
        return sum([ len(sub_dicts) for sub_dicts in self._dict.values() ])
    
    def to_dict(self, keys: Union[list, tuple], value: Any) -> dict:
        return dict(zip(self.key_names, keys)) | self.value2dict(value)
    
    def to_df(self) -> DataFrame:
        if self.value_names is None:
            return DataFrame(sum([
                [
                    dict(zip(self.key_names, keys)) | row 
                    for row in row_list
                ] for keys, row_list in self.__iter__(process=False)
            ], list()))
        if len(self.value_names) == 1:
            return DataFrame([ 
                dict(zip(self.key_names, keys)) | { self.value_names[0]: value }
                for keys, value in self.__iter__(process=False)
            ])
        return DataFrame([ 
            dict(zip(self.key_names, keys)) | dict(zip(self.value_names, value)) 
            for keys, value in self.__iter__(process=False)
        ])

    def save(self, directory: Union[str, Path]) -> tuple[str, str]:
        assert self.save_filename is not None, f"{type(self).__name__} has no save filename"
        path = Path(directory) / self.save_filename
        self.to_df().to_csv(path, index=False)
        return type(self).__name__, str(path)

    def __repr__(self) -> str:
        return repr(self.to_df()) 
