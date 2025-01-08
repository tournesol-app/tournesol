import numpy as np

from typing import Optional, Union, Mapping
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

    def order_by_entities(self) -> "Comparisons": # key_names == ["entity_name", "other_name", *]
        """ Returns an object Comparison, with the same set of comparisons,
        but now ordered by entities. Key names in self are replugged into the result,
        except for "left_name" and "right_name". Instead, an "other_name" is added
        to account for the other entity that the comparison is against.
        Moreover, we add an entry to each dict, which says whether "entity_name" 
        was the left or the right video.
        
        Returns
        -------
        ordered_comparisons: Comparisons
            With key_names == ["entity_name", "other_name", *]
        """
        if "entity_name" in self.key_names:
            key_names = ["entity_name", "other_name"] + [ 
                kn for kn in key_names 
                if kn not in ("entity_name", "other_name", "left_name", "right_name")
            ]
            return self.reorder_keys(key_names)
        assert "left_name" in self.key_names and "right_name" in self.key_names, "" \
            "Comparisons must have columns `left_name` and `right_name`"
        key_names = ["entity_name", "other_name"] + [ 
            kn for kn in self.key_names if kn not in ("left_name", "right_name") 
        ]
        result = Comparisons(key_names=key_names)
        left_key_index = self.key_names.index("left_name")
        right_key_index = self.key_names.index("right_name")
        for keys, comparison_list in self:
            for comparison in comparison_list:
                left_name, right_name = keys[left_key_index], keys[right_key_index]
                non_entity_keys = [ 
                    key for index, key in enumerate(keys) 
                    if index not in (left_key_index, right_key_index) 
                ]
                new_comparison = dict(zip(self.key_names, keys)) | dict(comparison)
                result.add_row(
                    [left_name, right_name] + non_entity_keys,  
                    new_comparison | dict(location="left")
                )
                result.add_row(
                    [right_name, left_name] + non_entity_keys,
                    new_comparison | dict(location="right")
                )
        return result

    def compared_entity_indices(self, entity_name2index: dict[str, int]) -> dict[str, list[int]]:
        key_indices = { loc: self.key_names.index(f"{loc}_name") for loc in ("left", "right") }
        return {
            location: [ entity_name2index[keys[key_indices[location]]] for keys, _ in self ] 
            for location in ("left", "right")
        }
    
    def normalized_comparisons(self) -> Series:
        df = self.to_df()
        return df["comparison"] / df["comparison_max"]
