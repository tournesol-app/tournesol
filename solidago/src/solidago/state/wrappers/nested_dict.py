from typing import Union, Optional, Callable
from pathlib import Path
from pandas import DataFrame, Series

import pandas as pd


class NestedDict:
    def __init__(self, 
        args_names: list[str], 
        values_names: list[str],
        d: Optional[Union[dict, DataFrame]]=None,
        save_filename: Optional[str]=None,
    ):
        """ Defines a nested dict for sparse data storage of values with multiple keys """
        assert len(args_names) >= 1
        self.args_names = args_names
        self.values_names = values_names
        self._dict = dict()
        self.save_filename = save_filename
        
        if isinstance(d, dict):
            for key in d:
                self._dict[str(key)] = type(self)(
                    arg_names=args_names[1:], values_names=values_names, d=d[str(key)]
                ) if len(args_names) > 1 else self.value_process(d[str(key)])
        if isinstance(d, DataFrame):
            for _, row in d.iterrows():
                args = [row[arg_name] for arg_name in args_names]
                self[args] = self.value_process(row)
    
    def default_value(self) -> "OutputValue":
        return None
    
    def value_process(self, value) -> "OutputValue":
        if isinstance(value, Series) and len(self.values_names) == 1:
            return value[self.values_names[0]]
        elif isinstance(value, Series):
            return (value[name] for name in self.values_names)
        return value
        
    def value2list(self, value) -> list:
        return [value]
    
    def get(self, *keys) -> Union["NestedDict", "OutputValue"]:
        assert len(keys) <= len(self.args_names), (keys, repr(self))
        if str(keys[0]) not in self._dict:
            return self.default_value
        if len(keys) == 1:
            return self._dict[str(keys[0])]
        return self._dict[str(keys[0])].get(*keys[1:])
    
    def __getitem__(self, keys: Union[str, tuple, list]) -> Union["NestedDict", "OutputValue"]:
        return self.get(keys) if isinstance(keys, str) else self.get(*keys)
    
    def __setitem__(self, keys: Union[str, tuple, list], value: "OutputValue") -> None:
        if len(keys) == 1:
            assert len(self.args_names) == 1
            self._dict[str(keys[0])] = self.value_process(value)
            return None
        assert len(keys) == len(self.args_names), (keys, self.args_names)
        if str(keys[0]) not in self._dict:
            self._dict[str(keys[0])] = type(self)(args_names=self.args_names[1:], values_names=self.values_names)
        self._dict[str(keys[0])][keys[1:]] = self.value_process(value)

    @classmethod
    def load(cls, filename: str) -> "NestedDict":
        return cls(pd.read_csv(filename, keep_default_na=False))

    def __iter__(self):
        if len(self.args_names) == 1:
            for key, value in self._dict.items():
                yield [key], value
        else:
            for key in self._dict:
                for subkeys, value in self._dict[key]:
                    keys = [key] + subkeys
                    assert len(keys) == len(self.args_names), (keys, self.args_names)
                    yield keys, value

    def __len__(self):
        if len(self.args_names) == 1:
            return len(self._dict)
        return sum([ len(sub_dicts) for sub_dicts in self._dict.values() ])

    def to_df(self) -> DataFrame:
        return DataFrame([
            args + self.value2list(value)
            for args, value in self
        ], columns=self.args_names + self.values_names)

    def save(self, directory: Union[str, Path]) -> tuple[str, str]:
        assert self.save_filename is not None, f"{type(self).__name__} has no save filename"
        path = Path(directory) / self.save_filename
        self.to_df().to_csv(path)
        return type(self).__name__, str(path)

    def __repr__(self) -> str:
        return repr(self.to_df()) 

    def __contains__(self, args: Union[str, tuple, list]) -> bool:
        if isinstance(args, str):
            return args in self._dict
        if args[0] not in self._dict:
            return False
        return args[1:] in self._dict[args[0]]
