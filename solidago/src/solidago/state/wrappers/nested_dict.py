from typing import Union, Optional, Callable
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce

import pandas as pd


class NestedDict:
    def __init__(self, 
        keys_names: list[str], 
        values_names: list[str],
        d: Optional[Union["NestedDict", dict, DataFrame]]=None,
        save_filename: Optional[str]=None,
    ):
        """ Defines a nested dict for sparse data storage of values with multiple keys """
        assert len(keys_names) >= 1
        self.keys_names = keys_names
        self.values_names = values_names
        self._dict = dict()
        self.save_filename = save_filename
        
        if isinstance(d, NestedDict):
            for key in d._dict:
                self._dict[str(key)] = d[str(key)]
        elif isinstance(d, dict):
            for key in d:
                self._dict[str(key)] = type(self)(
                    keys_names=keys_names[1:], values_names=values_names, d=d[str(key)], save_filename=None
                ) if len(keys_names) > 1 else self.value_process(d[str(key)])
        elif isinstance(d, DataFrame):
            for _, row in d.iterrows():
                keys = [row[key_name] for key_name in keys_names]
                value = row[values_names[0]] if len(values_names) == 1 else [row[name] for name in values_names]
                self[keys] = self.value_process(value)
    
    def default_value(self) -> "OutputValue":
        return None
    
    def value_process(self, value) -> "OutputValue":
        return value
        
    def value2list(self, value) -> list:
        return [value]
    
    def get(self, *keys, default_value: bool=True) -> Union["NestedDict", "OutputValue"]:
        assert len(keys) <= len(self.keys_names), (keys, repr(self))
        out_keys_names = [ 
            n for n, key in zip(self.keys_names[:len(keys)], keys)
            if key == any or isinstance(key, (set, tuple, list))
        ] + self.keys_names[len(keys):]
        if len(keys) == 0:
            return self
        if keys[0] == any and len(self.keys_names) == 1:
            return self
        if keys[0] == any: # len(self.keys_names) > 1 and len(out_keys_names) > 0
            d = { key: subdict.get(*keys[1:], default_value=(len(out_keys_names) == 0)) for key, subdict in self._dict.items() }
            d = { key: subdict for key, subdict in d.items() if len(subdict) > 0  }
            return type(self)(keys_names=out_keys_names, values_names=self.values_names, d=d, save_filename=None)
        if isinstance(keys[0], (set, tuple, list)):
            d = { key: subdict.get(*keys[1:], default_value=(len(out_keys_names) == 0)) for key, subdict in self._dict.items() if key in keys[0] }
            d = { key: subdict for key, subdict in d.items() if len(subdict) > 0 }
            return type(self)(keys_names=out_keys_names, values_names=self.values_names, d=d, save_filename=None)
        if str(keys[0]) not in self._dict:
            return self.default_value() if default_value else dict()
        if len(keys) == 1:
            return self._dict[str(keys[0])]
        return self._dict[str(keys[0])].get(*keys[1:])

    def __contains__(self, keys: Union[str, tuple, list, dict]) -> bool:
        if isinstance(keys, str):
            return keys in self._dict
        elif isinstance(keys, dict):
            if self.keys_names[0] in keys:
                key = keys[self.keys_names[0]]
                del keys[self.keys_names[0]]
                return keys in self[key]
            if any({ key_name in self.keys_names for key_name in keys }):
                return any({ keys in subdict for _, subdict in self._dict.items() })
            return True
        elif len(keys) == 1:
            return keys[0] in self._dict
        assert len(keys) <= len(self.keys_names), (keys, self.keys_names, self)
        if keys[0] not in self._dict:
            return False
        return keys[1:] in self._dict[keys[0]]
    
    def __getitem__(self, keys: Union[str, tuple, list, dict]) -> Union["NestedDict", "OutputValue"]:
        if isinstance(keys, dict):
            keys = [(keys[name] if name in keys else any) for name in self.args_names]
        return self.get(keys) if keys == any or isinstance(keys, str) else self.get(*keys)

    def __contains__(self, keys: Union[str, tuple, list, dict]) -> bool:
        if isinstance(keys, str):
            return keys in self._dict
        elif isinstance(keys, dict):
            if self.keys_names[0] in keys:
                key = keys[self.keys_names[0]]
                del keys[self.keys_names[0]]
                return keys in self[key]
            if any({ key_name in self.keys_names for key_name in keys }):
                return any({ keys in subdict for _, subdict in self._dict.items() })
            return True
        elif len(keys) == 1:
            return keys[0] in self._dict
        assert len(keys) <= len(self.keys_names), (keys, self.keys_names, self)
        if keys[0] not in self._dict:
            return False
        return keys[1:] in self._dict[keys[0]]
    
    def get_set(self, key_name: str) -> set[str]:
        assert key_name in self.keys_names, (key_name, self.keys_names)
        if key_name == self.keys_names[0]:
            return set(self._dict)
        return reduce(lambda subdict, s: subdict.get_key(key_name) | s, self._dict.values(), set())
    
    def set(self, keys: Union[str, tuple, list], value: "OutputValue", value_process: bool=True) -> None:
        if len(keys) == 1:
            assert len(self.keys_names) == 1, (keys, self.keys_names, self)
            self._dict[str(keys[0])] = self.value_process(value) if value_process else value
            return None
        assert len(keys) == len(self.keys_names), (keys, self.keys_names)
        if str(keys[0]) not in self._dict:
            self._dict[str(keys[0])] = type(self)(keys_names=self.keys_names[1:], values_names=self.values_names)
        self._dict[str(keys[0])].set(keys[1:], value, value_process)
        
    def __setitem__(self, keys: Union[str, tuple, list], value: "OutputValue") -> None:
        self.set(keys, value)

    @classmethod
    def load(cls, filename: str) -> "NestedDict":
        return cls(pd.read_csv(filename, keep_default_na=False))

    def __iter__(self):
        if len(self.keys_names) == 1:
            for key, value in self._dict.items():
                yield [key], value
        else:
            for key in self._dict:
                for subkeys, value in self._dict[key]:
                    keys = [key] + subkeys
                    assert len(keys) == len(self.keys_names), (keys, self.keys_names)
                    yield keys, value

    def __len__(self):
        if len(self.keys_names) == 1:
            return len(self._dict)
        return sum([ len(sub_dicts) for sub_dicts in self._dict.values() ])
    
    def to_df(self) -> DataFrame:
        return DataFrame([
            keys + self.value2list(value)
            for keys, value in self
        ], columns=self.keys_names + self.values_names)

    def save(self, directory: Union[str, Path]) -> tuple[str, str]:
        assert self.save_filename is not None, f"{type(self).__name__} has no save filename"
        path = Path(directory) / self.save_filename
        self.to_df().to_csv(path)
        return type(self).__name__, str(path)

    def __repr__(self) -> str:
        return repr(self.to_df()) 
