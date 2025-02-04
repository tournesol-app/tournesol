from typing import Optional, Any

from .base import MadePublic


class AllPublic(MadePublic):
    def __init__(self, 
        data: Optional[Any]=None, 
        key_names=["username", "entity_name"],
        value_name="public",
        name="made_public",
        default_value=True,
        last_only=True,
        **kwargs
    ):
        super().__init__(data, key_names, value_name, name, default_value, last_only, **kwargs)
    
    def add_row(*args, **kwargs):
        pass
        
    def set(*args, **kwargs):
        pass

    def penalty(self, privacy_penalty: float, *keys) -> float:
        return 1

    @classmethod
    def load(cls, *args, **kwargs) -> "AllPublic":
        return cls()

    def save(self, *arg, **kwargs) -> tuple[str, str]:
        return type(self).__name__, None
