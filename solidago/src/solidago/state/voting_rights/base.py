from typing import Union, Optional
from pandas import DataFrame

from solidago.primitives.datastructure import NestedDictOfItems


class VotingRights(NestedDictOfItems):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        key_names=["username", "entity_name", "criterion"],
        value_name="voting_right",
        save_filename="voting_rights.csv"
    ):
        super().__init__(d, key_names, value_name, save_filename)
    
    def default_value(self) -> bool:
        return 0    
