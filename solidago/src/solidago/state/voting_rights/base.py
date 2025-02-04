from typing import Optional, Any

from solidago.primitives.datastructure import UnnamedDataFrame


class VotingRights(UnnamedDataFrame):
    def __init__(self, 
        data: Optional[Any]=None, 
        key_names=["username", "entity_name", "criterion"],
        value_name="voting_right",
        name="voting_rights",
        default_value=0,
        last_only=True,
        **kwargs
    ):
        super().__init__(key_names, value_name, name, default_value, last_only, data, **kwargs)
