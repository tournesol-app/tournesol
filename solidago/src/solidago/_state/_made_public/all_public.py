from typing import Optional, Union
from pandas import DataFrame
from pathlib import Path

from .base import MadePublic


class AllPublic(MadePublic):
    def __init__(self):
        super().__init__()
    
    def __getitem__(self, args: tuple[Union[str, "User"], Union[str, "Entity"]]) -> bool:
        return True
    
    def __setitem__(self, args: tuple[Union[str, "User"], Union[str, "Entity"]], public: bool=True) -> None:
        if not public:
            raise f"All public configuration does not allow private settings"

    @classmethod
    def load(cls, filename: Optional[str]="None") -> MadePublic:
        return cls()
    
    def to_df(self) -> DataFrame:
        return DataFrame()

    def save(self, directory: Union[str, Path]) -> tuple[str, dict]:
        return type(self).__name__, dict()
        
    def __repr__(self) -> str:
        return type(self).__name__
