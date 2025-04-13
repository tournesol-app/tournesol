from typing import Optional, Callable, Union, Any
from pandas import Series
import numbers

from solidago.primitives.datastructure import NestedDict, MultiKeyTable


class VotingRights(MultiKeyTable):
    name: str="voting_rights"
    value_cls: type=numbers.Number
    
    def __init__(self, 
        keynames: list[str]=["username", "entity_name", "criterion"], 
        init_data: Optional[Union[NestedDict, Any]]=None,
        parent_tuple: Optional[tuple["VotingRights", tuple, tuple]]=None,
        *args, **kwargs
    ):
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

    @classmethod
    def value_factory(cls):
        return 0
        
    @property
    def valuenames(self) -> tuple[str, str]:
        return ("voting_right",)

    def series2value(self, previous_value: Any, row: Series) -> float:
        return row["voting_right"]
