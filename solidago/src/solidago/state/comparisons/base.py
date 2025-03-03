import numpy as np
import pandas as pd

from typing import Optional, Union, Mapping, Literal, Any
from pandas import DataFrame, Series

from solidago.primitives.datastructure import UnnamedDataFrame


class Comparison(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Comparisons(UnnamedDataFrame):
    row_cls: type=Comparison
    
    def __init__(self, 
        data: Optional[Any]=None,
        key_names=["username", "criterion", "left_name", "right_name"],
        value_names=None,
        name="comparisons",
        default_value=None,
        last_only=True,
        **kwargs
    ):
        super().__init__(data, key_names, value_names, name, default_value, last_only, **kwargs)
        
    def get_evaluators(self, entity: Union[str, "Entity"]) -> set[str]:
        evaluators = set(self.get(left_name=entity)["username"])
        return evaluators | set(self.get(right_name=entity)["username"])

    def order_by_entities(self, other_keys_first: bool=True) -> "Comparisons":
        """ Returns an object Comparison, with the same set of comparisons,
        but now ordered by entities. Key names in self are replugged into the result,
        except for "left_name" and "right_name". Instead, an "other_name" is added
        to account for the other entity that the comparison is against.
        Moreover, we add an entry to each dict, which says whether "entity_name" 
        was the left or the right video.
        
        Returns
        -------
        ordered_comparisons: Comparisons
            With key_names == ["entity_name", "other_name", *] or [*, "entity_name", "other_name"]
            depending on parameter other_keys_first
        """
        if "entity_name" in self.key_names:
            return self
        assert "left_name" in self.key_names and "right_name" in self.key_names, "" \
            "Comparisons must have columns `left_name` and `right_name`"
        
        left, right = self.copy(), self.copy()
        left[["entity_name", "other_name"]] = self[["left_name", "right_name"]]
        left["location"] = "left"
        right[["entity_name", "other_name"]] = self[["right_name", "left_name"]]
        right["location"] = "right"
        right["value"] = - self["value"]
        
        key_names = [ kn for kn in self.key_names if kn not in ["left_name", "right_name"] ]
        new_key_names = ["entity_name", "other_name"]
        key_names = (key_names + new_key_names) if other_keys_first else (new_key_names + key_names)
        
        return type(self)(pd.concat([left, right]), key_names=key_names)

    def compared_entity_indices(self, entity_name2index: dict[str, int]) -> dict[str, list[int]]:
        key_indices = { loc: self.key_names.index(f"{loc}_name") for loc in ("left", "right") }
        return {
            location: [ 
                entity_name2index[keys[key_indices[location]]] 
                for keys, _ in self.iter(last_only=self.meta._last_only)
            ] for location in ("left", "right")
        }
    
    def normalized_comparisons(self) -> np.ndarray:
        return np.array() if self.empty else np.array(self["value"] / self["max"])

    def to_comparison_dict(self, 
        entities: "Entities", 
        last_only: Optional[bool]=None,
    ) -> list[tuple[list, np.array]]:
        """
        Returns
        -------
        result: list[tuple[np.array, np.array]]
            result[i] is a pair compared_indices, normalized_comparisons
            which respectively contain the indices of entities compared to entities.iloc[i]
            and the normalized comparisons against these compared entities
        """
        result = list()
        last_only = self.meta._last_only if last_only is None else last_only
        comparisons = self.last_only() if last_only else self
        entity_ordered_comparisons = comparisons.order_by_entities().to_dict(["entity_name"])
        entity_name2index = { str(entity): index for index, entity in enumerate(entities) }
        for i, entity in enumerate(entities):
            comparisons = entity_ordered_comparisons[str(entity)]
            if len(comparisons) == 0:
                result.append((list(), np.array([])))
            else:
                result.append((
                    list(comparisons["other_name"].map(entity_name2index)),
                    np.array(comparisons.normalized_comparisons())
                ))
        return result
