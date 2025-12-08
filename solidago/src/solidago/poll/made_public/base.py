from typing import Optional, Callable, Union, Any
from pandas import Series

from solidago.primitives.datastructure import NestedDict, MultiKeyTable


class MadePublic(MultiKeyTable):
    name: str="made_public"
    value_cls: type=bool
    
    def __init__(self, 
        keynames: list[str]=["username", "entity_name"], 
        init_data: Optional[Union[NestedDict, Any]]=None,
        parent_tuple: Optional[tuple["MadePublic", tuple, tuple]]=None,
        *args, **kwargs
    ):
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

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
