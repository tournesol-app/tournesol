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

    def get_evaluators_by_criterion(self, entity: Union[str, "Entity"]) -> dict[str, set[str]]:
        evaluators = dict()
        for comparisons in (self[any, entity, any], self[any, any, entity]):
            for username, row_list in comparisons:
                for row in row_list:
                    criterion = row["criterion"] if "criterion" in row else "default"
                    if criterion not in evaluators:
                        evaluators[criterion] = set()
                    evaluators[criterion].add(username)
        return evaluators

    def order_by_entities(self) -> Comparisons:
        result = Comparisons(key_names=["entity"])
        assert "left_name" in self.key_names and "right_name" in self.key_names, "" \
            "Comparisons must have columns `left_name` and `right_name`"
        left_key_index = self.key_names.index("left_name")
        right_key_index = self.key_names.index("right_name")
        for keys, row_list in self:
            for row in row_list:
                left_name = keys[left_key_index]
                right_name = keys[right_key_index]
                new_row = dict(zip(self.key_names, keys)) | row
                result.add_row(left_name,  new_row | { "location": "left", "with": right_name })
                result.add_row(right_name, new_row | { "location": "right", "with": left_name })
        return result
