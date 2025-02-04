from typing import Optional, Any

from solidago.primitives.datastructure import UnnamedDataFrame


class Vouches(UnnamedDataFrame):
    def __init__(self, 
        data: Optional[Any]=None, 
        key_names=["by", "to", "kind"],
        value_names=["weight", "priority"],
        name="vouches",
        default_value=(0, - float("inf")),
        last_only=True,
        **kwargs
    ):
        super().__init__(key_names, value_names, name, default_value, last_only, data, **kwargs)
    
