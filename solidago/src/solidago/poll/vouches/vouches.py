from typing import Any
from pandas import Series

from solidago.primitives.datastructure import NestedDict, MultiKeyTable


class Vouches(MultiKeyTable):
    name: str="vouches"
    value_cls: type=tuple
    default_keynames: tuple = ("by", "to", "kind")
    
    @classmethod
    def value_factory(cls):
        return 0, - float("inf")

    @property
    def valuenames(self) -> tuple[str, str]:
        return "weight", "priority"

    def value2tuple(self, value: tuple[float, float]) -> tuple[float, float]:
        return value
        
    def value2series(self, value: tuple[float, float]) -> Series:
        return Series(dict(weight=value[0], priority=value[1]))
    
    def series2value(self, previous_value: Any, row: Series) -> tuple[float, float]:
        return row["weight"], row["priority"]

    def has_default_type(self) -> bool:
        return type(self) == Vouches and self.keynames == tuple(self.default_keynames)