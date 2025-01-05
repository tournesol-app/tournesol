from typing import Optional, Union
from pandas import DataFrame, Series

from solidago.primitives.datastructure import NestedDictOfRowLists


class Comparison(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Comparisons(NestedDictOfRowLists):
    row_cls: type=Comparison
    
    def __init__(self, 
        d: Optional[Union[NestedDictOfRowLists, dict, DataFrame]]=None, 
        key_names=["username", "criterion", "left_name", "right_name"],
        save_filename="comparisons.csv"
    ):
        super().__init__(d, key_names, save_filename)

    def default_value(self) -> list:
        return list()
    
    def process_stored_value(self, keys: list[str], stored_value: list[dict]) -> list[Comparison]:
        return [self.row_cls(v) for v in stored_value]
        
    def get_evaluators(self, entity: Union[str, "Entity"]) -> set[str]:
        evaluators = self[{ "left_name": entity }].get_set("username") 
        return evaluators | self[{ "right_name": entity }].get_set("username")

    def order_by_entities(self) -> "Comparisons":
        if "entity_name" in self.key_names:
            key_names = ["entity_name"] + [ kn for kn in key_names if kn != ["entity_name"] ]
            return self.reorder_keys(key_names)
        assert "left_name" in self.key_names and "right_name" in self.key_names, "" \
            "Comparisons must have columns `left_name` and `right_name`"
        result = Comparisons(key_names=["entity_name"])
        left_key_index = self.key_names.index("left_name")
        right_key_index = self.key_names.index("right_name")
        for keys, row_list in self:
            for row in row_list:
                left_name = keys[left_key_index]
                right_name = keys[right_key_index]
                new_row = dict(zip(self.key_names, keys)) | dict(row)
                result.add_row(left_name,  new_row | { "location": "left", "with": right_name })
                result.add_row(right_name, new_row | { "location": "right", "with": left_name })
        return result
