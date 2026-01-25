from typing import Any
from pandas import Series

from solidago.primitives.datastructure import NestedDict, MultiKeyTable


class MadePublic(MultiKeyTable):
    name: str = "made_public"
    value_cls: type = bool
    default_keynames: tuple = ("username", "entity_name")

    @classmethod
    def value_factory(cls):
        return False
        
    @property
    def valuenames(self) -> tuple:
        return ("public",)
    
    def series2value(self, previous_value: Any, row: Series) -> bool:
        return row["public"]

    def penalty(self, privacy_penalty: float, *args, **kwargs) -> float:
        return 1 if self.get(*args, **kwargs) else privacy_penalty

    def has_default_type(self) -> bool:
        return type(self) == MadePublic and self.keynames == tuple(self.default_keynames)