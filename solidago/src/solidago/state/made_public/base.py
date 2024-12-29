from typing import Union, Optional
from pandas import DataFrame

from solidago.primitives.datastructure.nested_dict import NestedDict


class MadePublic(NestedDict):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        key_names=["username", "entity_name"],
        value_names=["public"],
        save_filename="made_public.csv"
    ):
        super().__init__(d, key_names, value_names, save_filename)
    
    def default_value(self) -> tuple[float, float]:
        return False

    def __setitem__(self, keys: Union[str, tuple, list], value: bool) -> None:
        if value:
            super(MadePublic, self).__setitem__(keys, value)

    def get(self, *keys):
        if len(keys) == 1 and self.key_names == ["username", "entity_name"]:
            return set(self._dict[keys[0]]._dict.keys())
        return super(MadePublic, self).get(keys)
