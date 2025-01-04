from typing import Union, Optional, Callable, Any, Iterable
from types import BuiltinFunctionType
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce

import pandas as pd

from .nested_dict import NestedDict, NestedKeyError


class NestedDictOfItems(NestedDict):
    def __init__(self, 
        d: Optional[Union["NestedDict", dict, DataFrame]]=None,
        key_names: list[str]=["key"], 
        value_name: str="value", 
        save_filename: Optional[str]=None,
        default_value: Optional[Any]=None
    ):
        """ Defines a nested dict for sparse data storage of values with multiple keys,
        where the values are themselves lists of dict """
        assert isinstance(value_name, str)
        self.value_name = value_name
        self._default_value = default_value
        super().__init__(d=d, key_names=key_names, save_filename=save_filename)

    def default_value(self) -> Any:
        return self._default_value

    def add_row(self, keys: list[str], row: Union[dict, Series]) -> None:
        self[keys] = row[self.value_name]

    def get_set(self, key_name: str, default_value: Optional[str]=None) -> set:
        try:
            return super().get_set(key_name, default_value)
        except NestedKeyError:
            if value_name not in self.value_name:
                raise NestedKeyError(key_name)
            return { value for _, value in self }

    def to_rows(self, kwargs: Optional[dict]) -> list[dict]:
        if row_kwargs is None:
            row_kwargs = dict()
        return [ 
            dict(zip(self.key_names, keys)) | { self.value_name: value }
            for keys, value in self.__iter__(process=False)
        ]
        
