from typing import Optional, Callable, Union, Any
from pandas import Series

from solidago.primitives.datastructure import NestedDict, MultiKeyTable


class VotingRights(MultiKeyTable):
    name: str="voting_rights"
    value_factory: Callable=lambda: 0
    
    def __init__(self, 
        keynames: list[str]=["username", "entity_name", "criterion"], 
        init_data: Optional[Union[NestedDict, Any]]=None,
        parent_tuple: Optional[tuple["VotingRights", tuple, tuple]]=None,
        *args, **kwargs
    ):
        super().__init__(keynames, init_data, parent_tuple, *args, **kwargs)

    def value2series(self, value: float) -> Series:
        return Series(dict(voting_right=value))
    
    def series2value(self, previous_value: Any, row: Series) -> float:
        return row["voting_right"]
