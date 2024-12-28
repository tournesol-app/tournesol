from typing import Optional, Union
from pandas import DataFrame

from solidago.state.wrappers.nested_dict import NestedDict


class Assessments(NestedDict):    
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        keys_names=["username", "entity_name", "criterion_name"],
        values_names=["assessment", "assessment_min", "assessment_max"],
        save_filename="assessments.csv"
    ):
        super().__init__(keys_names, values_names, d, save_filename)

    def get_evaluators(self, entity: Union[str, "Entity"], criterion: Union[str, "Criterion"]) -> set[str]:
        return set(self[any, entity, criterion])
    
    def value_process(self, value: Union[int, float, tuple, list]) -> tuple[float, float, float]:
        if isinstance(value, (int, float)):
            return value, -float(inf), float(inf)
        assert len(value) == 3
        return tuple(value)
        
    def value2list(self, value: tuple[float, float]) -> list[float]:
        return list(self.value_process(value))
