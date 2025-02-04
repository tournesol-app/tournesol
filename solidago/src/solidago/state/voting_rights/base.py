from typing import Union, Optional
from pandas import DataFrame

from solidago.primitives.datastructure import UnnamedDataFrame


class VotingRights(UnnamedDataFrame):
    def __init__(self, 
        data: Optional[Union[dict, DataFrame]]=None, 
        key_names=["username", "entity_name", "criterion"],
        value_name="voting_right",
        save_filename="voting_rights.csv"
    ):
        super().__init__(key_names, value_name, save_filename, data=data, default_value=0)
