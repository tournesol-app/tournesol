from typing import Union, Optional
from pandas import DataFrame

from solidago.primitives.datastructure import NestedDictOfItems


class MadePublic(NestedDictOfItems):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        key_names=["username", "entity_name"],
        value_name="public",
        save_filename="made_public.csv"
    ):
        super().__init__(d, key_names, value_name, save_filename)
    
    def default_value(self) -> bool:
        return False
    
    def __setitem__(self, keys: Union[str, tuple, list], value: bool) -> None:
        if value:
            super().__setitem__(keys, value)
