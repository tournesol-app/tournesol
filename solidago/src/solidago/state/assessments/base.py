from typing import Optional, Callable, Union, Any
from pandas import Series

from solidago.primitives.datastructure import NestedDict, MultiKeyTable


class Assessment:
    def __init__(self, 
        value: float=float("nan"), 
        min: float=-float("inf"), 
        max: float=float("inf"), 
        **kwargs
    ):
        self.value = value
        self.min = min
        self.max = max
    
    @classmethod
    def from_series(cls, row: Series) -> "Assessment":
        return cls(**dict(row))

    def to_series(self) -> Series:
        return Series(dict(value=self.value, min=self.min, max=self.max))


class Assessments(MultiKeyTable):
    name: str="assessments"
    value_factory: Callable=lambda: None
    value_cls: type=Assessment
    
    def __init__(self, 
        keynames: list[str]=["username", "criterion", "entity_name"], 
        init_data: Optional[Union[NestedDict, Any]]=None,
        parent_tuple: Optional[tuple["Assessments", tuple, tuple]]=None,
        *args, **kwargs
    ):
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

    def value2series(self, assessment: Assessment) -> Series:
        return assessment.to_series()
    
    def series2value(self, previous_stored_value: Any, row: Series) -> Assessment:
        return Assessment.from_series(row)

    def get_evaluators(self, entity: Union[str, "Entity"]) -> set[str]:
        return { username for username in self.get(entity_name=entity).keys("username") }
