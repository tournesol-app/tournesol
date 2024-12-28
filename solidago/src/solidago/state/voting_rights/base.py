from typing import Union, Optional
from pandas import DataFrame

from solidago.state.wrappers import NestedDict


class VotingRights(NestedDict):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        keys_names=["username", "entity_name", "criterion_name"],
        values_names=["voting_right"],
        save_filename="voting_rights.csv"
    ):
        super().__init__(keys_names, values_names, d, save_filename)
    
    def default_value(self) -> float:
        return 0
