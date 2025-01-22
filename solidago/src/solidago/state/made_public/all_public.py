from typing import Optional, Union
from pandas import DataFrame
from pathlib import Path

from .base import MadePublic
from solidago.primitives.datastructure import NestedDictOfItems


class AllPublic(NestedDictOfItems):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        key_names=["username", "entity_name"],
        value_name="public",
        save_filename="made_public.csv"
    ):
        super().__init__(d, key_names, value_name, save_filename, default_value=True)
    
    def __setitem__(self, keys: Union[str, tuple, list], value: bool) -> None:
        pass

    def penalty(self, privacy_penalty: float, *keys) -> float:
        return 1
