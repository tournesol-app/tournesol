from typing import Union, Optional
from pandas import DataFrame

from solidago.primitives.datastructure.nested_dict import NestedDict


class VotingRights(NestedDict):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        key_names=["username", "entity_name", "criterion"],
        value_names=["voting_right"],
        save_filename="voting_rights.csv"
    ):
        super().__init__(d, key_names, value_names, save_filename)
    
    def default_value(self) -> float:
        return 0
