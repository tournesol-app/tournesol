from typing import Optional, Any

from solidago.primitives.datastructure import UnnamedDataFrame


class MadePublic(UnnamedDataFrame):
    def __init__(self, 
        data: Optional[Any]=None, 
        key_names=["username", "entity_name"],
        value_name="public",
        name="made_public",
        default_value=False,
        last_only=True,
        **kwargs
    ):
        super().__init__(key_names, value_name, name, default_value, last_only, data, **kwargs)

    def penalty(self, privacy_penalty: float, *args, **kwargs) -> float:
        return 1 if self.get(*args, **kwargs) else privacy_penalty
