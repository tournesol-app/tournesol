from typing import Union, Optional
from pandas import DataFrame, Series

from solidago.state.wrappers import NestedDict


class VotingRights(NestedDict):
    def __init__(self, 
        d: Optional[Union[dict, DataFrame]]=None, 
        args_names=["username", "entity_id", "criterion_id"],
        values_names=["voting_right"],
    ):
        super().__init__(args_names, values_names, d, "voting_rights.csv")
    
    def default_value(self) -> tuple[float, float]:
        return 0
