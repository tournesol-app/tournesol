from .base import MadePublic


class AllPublic(MadePublic):
    def __init__(self, keynames: list[str]=["username", "entity_name"], *args, **kwargs):
        super().__init__(keynames, *args, **kwargs)
    
    def add_row(*args, **kwargs):
        pass
        
    def set(*args, **kwargs):
        pass

    def penalty(self, privacy_penalty: float, *keys) -> float:
        return 1

    @classmethod
    def load(cls, directory: str, *args, **kwargs) -> "AllPublic":
        return cls(*args, **kwargs)

    def save(self, *arg, **kwargs) -> tuple[str, dict]:
        return type(self).__name__, dict(keynames=self.keynames)
