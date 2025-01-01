from typing import Union, Optional
from pandas import DataFrame

from solidago.primitives.datastructure.nested_dict import NestedDict


class VotingRights(NestedDict, VotingRights):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        key_names=["username", "entity_name"],
        value_names=None,
        save_filename="voting_rights.csv"
    ):
        super().__init__(d, key_names, value_names, save_filename)
    
    def default_value(self) -> bool:
        return dict()
    
    def process_stored_value(self, keys: list[str], stored_value: list[dict]) -> dict[str, float]:
        return {
            (row["criterion"] if "criterion" in row else "default"): row["voting_right"] 
            for row in stored_value 
        }
