from typing import Union, Optional, Callable, Any, Iterable
from types import BuiltinFunctionType
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce

import pandas as pd

from .nested_dict import NestedDict, NestedKeyError


class NestedDictOfTuples(NestedDict):
    def __init__(self, 
        d: Optional[Union["NestedDict", dict, DataFrame]]=None,
        key_names: list[str]=["key"], 
        value_names: list[str]=["value"], 
        save_filename: Optional[str]=None,
    ):
        """ Defines a nested dict for sparse data storage of values with multiple keys,
        where the values are themselves lists of dict """
        assert isinstance(value_names, (tuple, list))
        self.value_names = value_names
        super().__init__(d=d, key_names=key_names, save_filename=save_filename)

    def add_row(self, keys: list[str], row: Union[dict, Series]) -> None:
        self[keys] = tuple([row[name] for name in self.value_names])

    def sanitize(self, value: Any) -> tuple:
        return tuple(value)

    def get_set(self, key_name: str, default_value: Optional[str]=None) -> set:
        try:
            return super().get_set(key_name, default_value)
        except NestedKeyError:
            if value_name not in self.value_names:
                raise NestedKeyError(key_name)
            value_name_index = self.value_names.index(value_name)
            return { values[value_name_index] for _, values in self }

    def to_rows(self, row_kwargs: Optional[dict]=None) -> list[dict]:
        if row_kwargs is None:
            row_kwargs = dict()
        return [ 
            dict(zip(self.key_names, keys)) | dict(zip(self.value_names, value)) | row_kwargs
            for keys, value in self.__iter__(process=False)
        ]
