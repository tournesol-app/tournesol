import numpy as np

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
        name="comparisons",
        last_only=True,
        **kwargs
    ):
        super().__init__(key_names, None, name, None, last_only, data, **kwargs)
        
    def get_evaluators(self, entity: Union[str, "Entity"]) -> set[str]:
        evaluators = set(self.get(left_name=entity)["username"])
        return evaluators | set(self.get(right_name=entity)["username"])

    def compared_entity_indices(self, 
        entity_name2index: dict[str, int], 
        last_only: bool=True,
    ) -> dict[str, list[int]]:
        key_indices = { loc: self.key_names.index(f"{loc}_name") for loc in ("left", "right") }
        return {
            location: [ 
                entity_name2index[keys[key_indices[location]]] 
                for keys, _ in self.iter(last_only=last_only)
            ] for location in ("left", "right")
        }
    
    def normalized_comparisons(self) -> Series:
        return Series() if self.empty else self["comparison"] / self["comparison_max"]

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
