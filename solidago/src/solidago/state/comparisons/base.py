from typing import Optional, Union
from pandas import DataFrame

from solidago.state.wrappers.nested_dict import NestedDict


class Comparisons(NestedDict):    
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        keys_names=["username", "left_name", "right_name", "criterion_name"],
        values_names=["comparison", "comparison_max"],
        save_filename="comparisons.csv"
    ):
        super().__init__(keys_names, values_names, d, save_filename)

    def get_evaluators(self, entity: Union[str, "Entity"], criterion: Union[str, "Criterion"]) -> set[str]:
        return self[any, entity, any, criterion].get_set("username") | self[any, any, entity, criterion].get_set("username")
    
    def value_process(self, value: Union[int, float, tuple, list]) -> tuple[float, float]:
        if isinstance(value, (int, float)):
            return value, float(inf)
        assert len(value) == 2, value
        return tuple(value)
        
    def value2list(self, value: tuple[float, float]) -> list[float]:
        return list(self.value_process(value))
