from abc import ABC, abstractmethod
from typing import Union, Optional, Callable, Any, Iterable
from types import BuiltinFunctionType, SimpleNamespace
from pathlib import Path
from pandas import DataFrame, Series
from functools import reduce

import pandas as pd


class UnnamedDataFrameDict:
    
    def __init__(self, 
        *args, 
        df_cls: type=DataFrame, 
        main_key_names=list[str], 
        sub_key_names=list[str], 
        **kwargs
    ):
        self.dict = dict(*args, **kwargs)
        self.df_cls = df_cls
        self.main_key_names = main_key_names
        self.sub_key_names = sub_key_names
        
    def __getitem__(self, key: Union[Any, tuple[str]]) -> DataFrame:
        keys = tuple(str(k) for k in key) if isinstance(key, tuple) else str(key)
        return self.dict[keys] if keys in self.dict else self.df_cls()
    
    def __repr__(self) -> str:
        return "\n\n".join([ f"{key}:\n{value}" for key, value in self.dict.items() ])
    
    def __iter__(self) -> Iterable:
        for keys, value in self.dict.items():
            yield keys, value
