import numpy as np

from typing import Optional, Union, Mapping, Literal
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
        
        def invert(comparison):
            if "comparison" in comparison:
                comparison["comparison"] = - comparison["comparison"]
            return comparison
        key_names = ["entity_name", "other_name"] + [ 
            kn for kn in self.key_names if kn not in ("left_name", "right_name") 
        ]
        result = Comparisons(key_names=key_names)
        left_key_index = self.key_names.index("left_name")
        right_key_index = self.key_names.index("right_name")
        for keys, comparison in self:
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
                invert(new_comparison) | dict(location="right")
            )
        return result

    def compared_entity_indices(self, 
        entity_name2index: dict[str, int], 
        last_comparison_only: bool=True,
    ) -> dict[str, list[int]]:
        key_indices = { loc: self.key_names.index(f"{loc}_name") for loc in ("left", "right") }
        returns = "last_row" if last_comparison_only else "rows"
        return {
            location: [ 
                entity_name2index[keys[key_indices[location]]] 
                for keys, _ in self.iter(returns)
            ] for location in ("left", "right")
        }
    
    def normalized_comparisons(self, last_comparison_only: bool) -> Series:
        df = self.to_df(last_row_only=last_comparison_only)
        if df.empty:
            return Series()
        return df["comparison"] / df["comparison_max"]

    def to_comparison_dict(self, 
        entities: "Entities", 
        last_comparison_only: bool,
    ) -> list[tuple[np.array, np.array]]:
        """
        Returns
        -------
        comparison_dict: dict[str, tuple[Series, Series]]
            comparison_dict[entity_name] is a pair compared_indices, normalized_comparisons
            which respectively contain the indices of compared entities
            and the normalized comparisons against these compared entities
        """
        result = list()
        entity_ordered_comparisons = self.order_by_entities()
        entity_name2index = { str(entity): index for index, entity in enumerate(entities) }
        for i, entity in enumerate(entities):
            comparisons = entity_ordered_comparisons[str(entity)]
            if len(comparisons) == 0:
                result.append((list(), np.array([])))
            else:
                df = comparisons.to_df(last_row_only=last_comparison_only)
                result.append((
                    list(df["other_name"].map(entity_name2index)),
                    np.array(comparisons.normalized_comparisons(last_comparison_only))
                ))
        return result
