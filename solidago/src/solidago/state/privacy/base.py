from typing import Optional, Union
from pathlib import Path

import pandas as pd


class Privacy:
    def __init__(self, d: Union[dict, pd.DataFrame]=dict()):
        self._dict = d if isinstance(d, dict) else dict()
        if isinstance(d, pd.DataFrame):
            for _, r in d.iterrows():
                self[r["username"], r["entity_id"]] = r["private"]
    
    def __getitem__(self, args: tuple[Union[str, "User"], Union[str, "Entity"]]) -> Optional[bool]:
        username = args[0] if isinstance(args[0], str) else args[0].name
        entity_id = args[1] if isinstance(args[1], str) else args[1].id
        if username not in self._dict: return None
        if entity_id not in self._dict[username]: return None
        return self._dict[username][entity_id]
    
    def __setitem__(self, args: tuple[Union[str, "User"], Union[str, "Entity"]], private: Optional[bool]):
        username = args[0] if isinstance(args[0], (str, int)) else args[0].name
        entity_id = args[1] if isinstance(args[1], (str, int)) else args[1].id
        if username not in self._dict: self._dict[username] = dict()
        if private is None:
            del self._dict[username][entity_id]
        else:
            self._dict[username][entity_id] = private
            
    @classmethod
    def load(cls, filename: str) -> "Privacy":
        return cls(pd.read_csv(filename, keep_default_na=False))
    
    def to_df(self):
        return pd.DataFrame([
            pd.Series({ "username": username, "entity_id": entity_id, "private": private })
            for username in self._dict
            for entity_id, private in self._dict[username].items()
        ])

    def save(self, directory: Union[str, Path]) -> Union[str, list, dict]:
        path = Path(directory) / "privacy.csv"
        self.to_df().to_csv(path)
        return str(path)
        
    def __repr__(self):
        return repr(self.to_df()) 
