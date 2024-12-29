from typing import Union, Optional
from pandas import DataFrame, Series

from solidago.primitives.datastructure.nested_dict import NestedDict


class Vouches(NestedDict):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        key_names=["by", "to", "kind"],
        value_names=["weight", "priority"],
        save_filename="vouches.csv"
    ):
        super().__init__(d, key_names, value_names, save_filename)
    
    def default_value(self) -> tuple[float, float]:
        return 0, - float("inf")
    
    def value_process(self, 
        value: Union[Series, int, float, tuple, list], 
        keys: Optional[list]=None
    ) -> tuple[float, float]:
        if isinstance(value, Series) and "priority" in value:
            return value["weight"], 0
        elif isinstance(value, Series):
            return value["weight"], value["priority"]            
        if isinstance(value, (int, float)):
            return value, 0
        assert len(value) == 2
        return tuple(value)
