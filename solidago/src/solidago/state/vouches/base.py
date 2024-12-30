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
