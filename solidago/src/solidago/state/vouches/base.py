from typing import Union, Optional
from pandas import DataFrame, Series

from solidago.state.wrappers import NestedDict


class Vouches(NestedDict):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        keys_names=["by", "to", "kind"],
        values_names=["weight", "priority"],
        save_filename="vouches.csv"
    ):
        super().__init__(keys_names, values_names, d, save_filename)
    
    def default_value(self) -> tuple[float, float]:
        return 0, - float("inf")
    
    def value_process(self, value: Union[Series, int, float, tuple, list]) -> tuple[float, float]:
        if isinstance(value, Series) and "priority" in value:
            return value["weight"], 0
        elif isinstance(value, Series):
            return value["weight"], value["priority"]            
        if isinstance(value, (int, float)):
            return value, 0
        assert len(value) == 2
        return tuple(value)
        
    def value2list(self, value: tuple[float, float]) -> list[float]:
        return list(self.value_process(value))

