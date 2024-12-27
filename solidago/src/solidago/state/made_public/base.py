from typing import Union, Optional
from pandas import DataFrame, Series

from solidago.state.wrappers import NestedDict


class MadePublic(NestedDict):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        args_names=["username", "entity_id"],
        values_names=["public"],
    ):
        super().__init__(args_names, values_names, d, "made_public.csv")
    
    def default_value(self) -> tuple[float, float]:
        return False

    def __setitem__(self, keys: Union[str, tuple, list], value: bool) -> None:
        if value:
            super(MadePublic, self).__setitem__(keys, value)

    def get(self, *keys):
        if len(keys) == 1 and self.args_names == ["username", "entity_id"]:
            return set(self._dict[keys[0]]._dict.keys())
        return super(MadePublic, self).get(keys)
