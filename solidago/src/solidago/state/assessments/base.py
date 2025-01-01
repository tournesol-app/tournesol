from typing import Optional, Union
from pandas import DataFrame, Series

from solidago.primitives.datastructure.nested_dict import NestedDict


class Assessment(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

class Assessments(NestedDict):
    def __init__(self, 
        d: Optional[Union[NestedDict, dict, DataFrame]]=None, 
        key_names=["username", "entity_name"],
        value_names=None,
        save_filename="assessments.csv"
    ):
        super().__init__(d, key_names, value_names, save_filename)

    def default_value(self) -> list:
        return list()
    
    def process_stored_value(self, keys: list[str], stored_value: list[dict]) -> list[Assessment]:
        return [Assessment(v) for v in stored_value]
        
    def get_evaluators(self, entity: Union[str, "Entity"]) -> set[str]:
        return set(self[any, entity])
    
    def get_evaluators_by_criterion(self, entity: Union[str, "Entity"]) -> dict[str, set[str]]:
        assessments = self[any, entity]
        evaluators = dict()
        for username, row_list in assessments:
            for row in row_list:
                criterion = row["criterion"] if "criterion" in row else "default"
                if criterion not in evaluators:
                    evaluators[criterion] = set()
                evaluators[criterion].add(username)
        return evaluators
