from typing import Union, Optional
from pathlib import Path

from .sequential import Sequential


class Identity(Sequential):
    def __init__(self):
        super().__init__()

    def save(self, filename: Optional[Union[str, Path]]=None) -> tuple[str, list]:
        j = type(self).__name__, list()
        if filename is not None:
            with open(filename, "w") as f:
                json.dump(j, f)
        return j
