from typing import Optional, Union
from pandas import DataFrame

from solidago.primitives.datastructure.nested_dict import NestedDict


class Assessments(NestedDict):    
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        key_names=["username", "entity_name"],
        value_names=None,
        save_filename="assessments.csv"
    ):
        super().__init__(d, key_names, value_names, save_filename)

    def get_evaluators(self, entity: Union[str, "Entity"]) -> set[str]:
        return set(self[any, entity])

    def value_process(self, value, keys: Optional[list]=None):
        return dict(value)
