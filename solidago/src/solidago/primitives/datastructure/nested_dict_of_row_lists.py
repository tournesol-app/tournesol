from typing import Union, Optional, Callable, Any, Iterable, Literal
from types import BuiltinFunctionType
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce

import pandas as pd

from .nested_dict import NestedDict, NestedKeyError


class NestedDictOfRowLists(NestedDict):
    row_cls: type=dict
    
    def __init__(self, 
        d: Optional[Union["NestedDict", dict, DataFrame]]=None,
        key_names: list[str]=["key"], 
        save_filename: Optional[str]=None,
    ):
        """ Defines a nested dict for sparse data storage of values with multiple keys,
        where the values are themselves lists of dicts (called "rows") """
        assert len(key_names) >= 1
        super().__init__(d=d, key_names=key_names, save_filename=save_filename)

    def default_value(self) -> Any:
        return list()
        
    def process_stored_value(self, keys: list[str], stored_value: Union[list, dict]) -> Any:
        if isinstance(stored_value, dict):
            return self.row_cls(stored_value)
        if isinstance(stored_value, list):
            return [self.process_stored_value(keys, v) for v in stored_value]
        return stored_value
        
    def add_row(self, keys: Union[str, list, tuple], row: Union[dict, Series]) -> None:
        keys = keys if isinstance(keys, (list, tuple)) else [str(keys)]
        assert len(keys) == len(self.key_names)
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
        assert len(keys) == len(self.key_names)
        self[keys] = self.get(*keys, process=False) + [dict()]
    
    def append(self, keys: list, row: dict) -> None:
        keys = keys if isinstance(keys, (list, tuple)) else [str(keys)]
        assert len(keys) == len(self.key_names)
        self[keys] = self.get(*keys) + [dict(row)]

    def __len__(self) -> int:
        if len(self.key_names) == 1:
            return sum([len(row_list) for _, row_list in self._dict.items()])
        return sum([ len(sub_dicts) for sub_dicts in self._dict.values() ])

    def to_rows(self, row_kwargs: Optional[dict]=None, last_row_only: bool=False) -> list[dict]:
        if row_kwargs is None:
            row_kwargs = dict()
        returns = "last_row" if last_row_only else "rows"
        def to_dict(row):
            from solidago._state import Score
            if isinstance(row, (dict, Series)):
                return dict(row)
            elif isinstance(row, Score):
                return row.to_dict()
            elif isinstance(row, Iterable):
                return { i: r for i, r in enumerate(row) }
            elif isinstance(row, (bool, int, float, str)):
                return dict(row=row)
            else:
                raise ValueError(type(row))
        return [
            dict(zip(self.key_names, keys)) | row_kwargs | to_dict(row)
            for keys, row in self.iter(returns=returns, value_process=False, key_process=False)
        ]

    def to_df(self, row_kwargs: Optional[dict]=None, last_row_only: bool=False) -> DataFrame:
        return DataFrame(self.to_rows(row_kwargs, last_row_only))

    def iter(self, 
        returns: Literal["rows", "row_list", "last_row"]="rows", 
        value_process: bool=True,
        key_process: bool=True,
    ) -> Iterable:
        if len(self.key_names) == 1:
            for key, row_list in self._dict.items():
                assert isinstance(row_list, list), (key, row_list)
                if returns == "rows":
                    for row in row_list:
                        yield (
                            key if key_process else [key],
                            self.process_stored_value([key], row) if value_process else row
                        )
                elif returns == "row_list":
                    yield key if key_process else [key], [
                        self.process_stored_value([key], row) if value_process else row
                        for row in row_list
                    ]
                elif returns == "last_row":
                    yield (
                        key if key_process else [key],
                        self.process_stored_value([key], row_list[-1]) if value_process else row_list[-1]
                    )
                else:
                    raise ValueError(f"Returns argument '{returns}' must be 'rows', 'row_list' or 'last_row'.")
        else:
            kwargs = dict(returns=returns, value_process=value_process, key_process=False)
            for key in self._dict:
                for subkeys, value in self._dict[key].iter(**kwargs):
                    yield [key] + subkeys, value

    def __iter__(self,
        returns: Literal["rows", "row_list", "last_row"]="rows", 
        value_process: bool=True,
        key_process: bool=True,
    ) -> Iterable:
        return self.iter(returns=returns, value_process=value_process, key_process=key_process)
