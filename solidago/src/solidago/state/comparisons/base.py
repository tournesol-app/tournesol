from typing import Optional, Union
from pandas import DataFrame, Series

from solidago.primitives.datastructure.nested_dict import NestedDict


class Comparison(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Comparisons(NestedDict):
    def __init__(self, 
        d: Optional[Union[NestedDict, dict, DataFrame]]=None, 
        key_names=["username", "left_name", "right_name"],
        value_names=None,
        save_filename="comparisons.csv"
    ):
        super().__init__(d, key_names, value_names, save_filename)

    def default_value(self) -> list:
        return list()
    
    def process_stored_value(self, keys: list[str], stored_value: list[dict]) -> list[Comparison]:
        return [Comparison(v) for v in stored_value]
        
    def get_evaluators(self, entity: Union[str, "Entity"]) -> set[str]:
        return self[any, entity, any].get_set("username") | self[any, any, entity].get_set("username")
