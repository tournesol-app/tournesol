from typing import Optional, Union
from pathlib import Path

import pandas as pd


class VotingRights:
    def __init__(self, d: Union[dict, pd.DataFrame]=dict()):
        self._dict = d if isinstance(d, dict) else dict()
        if isinstance(d, pd.DataFrame):
            for _, r in d.iterrows():
                self[r["username"], r["entity_id"], r["criterion"]] = r["voting_right"]
    
    def __getitem__(self, args: tuple[Union[str, "User"], Union[str, "Entity"], str]) -> float:
        username = args[0] if isinstance(args[0], str) else args[0].name
        entity_id = args[1] if isinstance(args[1], str) else args[1].id
        criterion = args[2]
        if username not in self._dict: return 0
        if entity_id not in self._dict[username]: return 0
        if criterion not in self._dict[username][entity_id]: return 0
        return self._dict[username][entity_id][criterion]
    
    def __setitem__(self, args: tuple[Union[str, "User"], Union[str, "Entity"], str], voting_right: float):
        username = args[0] if isinstance(args[0], str) else args[0].name
        entity_id = args[1] if isinstance(args[1], str) else args[1].id
        criterion = args[2]
        if username not in self._dict: self._dict[username] = dict()
        if entity_id not in self._dict[username]: self._dict[username][entity_id] = dict()
        self._dict[username][entity_id][criterion] = voting_right

    @classmethod
    def load(cls, filename: str) -> "VotingRights":
        return cls(pd.read_csv(filename, keep_default_na=False))
    
    def to_df(self):
        return pd.DataFrame([
            pd.Series({
                "username": username,
                "entity_id": entity_id,
                "criterion": criterion,
                "voting_right": voting_right
            })
            for username in self._dict
            for entity_id in self._dict[username]
            for criterion, voting_right in self._dict[username][entity_id].items()
        ])

    def save(self, directory: Union[str, Path]) -> Union[str, list, dict]:
        path = Path(directory) / "voting_rights.csv"
        self.to_df().to_csv(path)
        return str(path)
        
    def __repr__(self):
        return repr(self.to_df()) 
