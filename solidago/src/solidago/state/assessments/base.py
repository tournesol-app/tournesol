from typing import Optional, Union, Any
from pandas import DataFrame, Series

from solidago.primitives.datastructure import UnnamedDataFrame


class Assessment(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        

class Assessments(UnnamedDataFrame):
    row_cls: type=Assessment
    
    def __init__(self, 
        data: Optional[Any]=None,
        key_names=["username", "criterion", "entity_name"],
        value_names=None,
        name="assessments",
        default_value=None,
        last_only=True,
        **kwargs
    ):
        super().__init__(data, key_names, value_names, name, default_value, last_only, **kwargs)

    def get_evaluators(self, entity: Union[str, "Entity"]) -> set[str]:
        return set(self.get(entity_name=entity)["username"])
    
