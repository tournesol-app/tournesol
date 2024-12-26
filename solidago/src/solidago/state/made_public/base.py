from typing import Optional, Union
from pathlib import Path
from pandas import DataFrame, Series

import pandas as pd


class MadePublic:
    def __init__(self, d: Optional[Union[dict, DataFrame]]=None):
        self._dict = d if isinstance(d, dict) else dict()
        if isinstance(d, DataFrame):
            for _, r in d.iterrows():
                self[r["username"], r["entity_id"]] = r["public"]
    
    def __getitem__(self, 
        args: Union[
            Union[str, "User"],
            tuple[Union[str, "User"], Union[str, "Entity"]]
        ]
    ) -> Union[set[str], bool]:
        from solidago.state import User
        if isinstance(args, (str, User)):
            return set(self._dict[str(args)].keys()) if str(args) in self._dict else set()
        username, entity_id = str(args[0]), str(args[1])
        if username not in self._dict or entity_id not in self._dict[username]: return False
        return self._dict[username][entity_id]
    
    def __setitem__(self, args: tuple[Union[str, "User"], Union[str, "Entity"]], public: bool=True) -> None:
        username, entity_id = str(args[0]), str(args[1])
        if username not in self._dict and public:
            self._dict[username] = dict()
        if public is False:
            if username not in self._dict:
                return None
            if entity_id in self._dict[username]:
                del self._dict[username][entity_id]
            if not any(self._dict[username]):
                del self._dict[username]
        else:
            self._dict[username][entity_id] = public
            
    @classmethod
    def load(cls, filename: str) -> "PublicSettings":
        return cls(pd.read_csv(filename, keep_default_na=False))
    
    def to_df(self) -> DataFrame:
        return DataFrame([
            Series({ "username": username, "entity_id": entity_id, "public": True })
            for username in self._dict
            for entity_id in self._dict[username]
        ])

    def save(self, directory: Union[str, Path]) -> tuple[str, str]:
        path = Path(directory) / "public_settings.csv"
        self.to_df().to_csv(path, index=False)
        return type(self).__name__, str(path)
        
    def __repr__(self) -> str:
        return repr(self.to_df()) 
