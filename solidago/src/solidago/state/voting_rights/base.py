from typing import Union, Optional
from pandas import DataFrame

from solidago.primitives.datastructure.nested_dict import NestedDict


class VotingRights(NestedDict):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        key_names=["username", "entity_name"],
        value_names=["voting_right"],
        save_filename="voting_rights.csv"
    ):
        super().__init__(d, key_names, value_names, save_filename)
    
    def default_value(self) -> float:
        return 0


class MultiVotingRights(NestedDict):
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
        return { row["criterion"]: row["voting_right"] for row in stored_value }

    def __getitem__(self, 
        keys: Union[str, tuple, list, dict], 
        criterion: Optional[str]=None
    ) -> Union["MultiVotingRights", VotingRights, float]:
        values = super().__getitem__(keys)
        if criterion is None:
            return values
        if isinstance(values, dict):
            return values[criterion] if criterion in values else 0
        voting_rights = VotingRights(key_names=values.key_names, save_filename=None)
        for keys, v in values:
            if criterion in v:
                voting_rights[keys] = v[criterion]
        return voting_rights
