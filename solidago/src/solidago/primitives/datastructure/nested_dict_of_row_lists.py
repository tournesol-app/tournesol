from typing import Union, Optional, Callable, Any, Iterable
from types import BuiltinFunctionType
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce

import pandas as pd

from .nested_dict import NestedDict, NestedKeyError


class NestedDictOfRowLists(NestedDict):
    def __init__(self, 
        d: Optional[Union["NestedDict", dict, DataFrame]]=None,
        key_names: list[str]=["key"], 
        save_filename: Optional[str]=None,
    ):
        """ Defines a nested dict for sparse data storage of values with multiple keys,
        where the values are themselves lists of dicts (called "rows") """
        assert len(key_names) >= 1
        super().__init__(d=d, key_names=key_names, save_filename=save_filename)

    def add_row(self, keys: list[str], row: Union[dict, Series]) -> None:
        l = self.get(*keys) if keys in self else list()
        self[keys] = l + [dict(row)]

    def get_set(self, key_name: str, default_value: Optional[str]=None) -> set:
        try:
            return super().get_set(key_name, default_value)
        except NestedKeyError:
            return {
                row[key_name] if key_name in row else default_value
                for _, row_list in self
                for row in row_list if key_name in row or default_value is None
            }

    def add(self, *keys) -> None:
        self[keys] = self.get(*keys) + [dict()]
    
    def append(self, keys: list, row: dict) -> None:
        self[keys] = self.get(*keys) + [dict(row)]

    def __len__(self) -> int:
        if len(self.key_names) == 1:
            return sum([len(row_list) for _, row_list in self._dict.items()])
        return sum([ len(sub_dicts) for sub_dicts in self._dict.values() ])

    def to_rows(self, kwargs: Optional[dict]) -> list[dict]:
        if row_kwargs is None:
            row_kwargs = dict()
        return [
            dict(zip(self.key_names, keys)) | row_kwargs | row
            for keys, row_list in self.__iter__(process=False)
            for row in row_list
        ]

