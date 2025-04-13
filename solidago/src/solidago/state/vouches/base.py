from typing import Optional, Callable, Union, Any
from pandas import Series

from solidago.primitives.datastructure import NestedDict, MultiKeyTable


class Vouches(MultiKeyTable):
    name: str="vouches"
    value_cls: type=tuple
    
    def __init__(self, 
        keynames: list[str]=["by", "to", "kind"], 
        init_data: Optional[Union[NestedDict, Any]]=None,
        parent_tuple: Optional[tuple["Vouches", tuple, tuple]]=None,
        *args, **kwargs
    ):
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

    @classmethod
    def value_factory(cls):
        return 0, - float("inf")

    @property
    def valuenames(self) -> tuple[str, str]:
        return "weight", "priority"

    def value2tuple(self, value: tuple[float, float]) -> [float, float]:
        return value
        
    def value2series(self, value: tuple[float, float]) -> Series:
        return Series(dict(weight=value[0], priority=value[1]))
    
    def series2value(self, previous_value: Any, row: Series) -> tuple[float, float]:
        return row["weight"], row["priority"]
