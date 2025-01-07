from typing import Optional, Union
from pandas import DataFrame, Series

from solidago.primitives.datastructure import NestedDictOfRowLists


class Assessment(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

class Assessments(NestedDictOfRowLists):
    row_cls: type=Assessment
    
    def __init__(self, 
        d: Optional[Union[NestedDictOfRowLists, dict, DataFrame]]=None, 
        key_names=["username", "criterion", "entity_name"],
        save_filename="assessments.csv"
    ):
        super().__init__(d, key_names, save_filename)

    def default_value(self) -> list:
        return list()
    
    def process_stored_value(self, keys: list[str], stored_value: list[dict]) -> list[Assessment]:
        return [self.row_cls(v) for v in stored_value]
        
    def get_evaluators(self, entity: Union[str, "Entity"]) -> set[str]:
        return self[{ "entity_name": entity }].get_set("username")
    
