from typing import Optional, Union
from pathlib import Path
from pandas import DataFrame, Series

import pandas as pd


class VotingRights:
    def __init__(self, d: Optional[Union[dict, DataFrame]]=None):
        self._dict = d if isinstance(d, dict) else dict()
        if isinstance(d, DataFrame):
            for _, r in d.iterrows():
                self[r["username"], r["entity_id"], r["criterion_id"]] = r["voting_right"]
    
    def __getitem__(self, args: tuple[Union[str, "User"], Union[str, "Entity"], Union[str, "Criterion"]]) -> float:
        username, entity_id, criterion_id = str(args[0]), str(args[1]), str(args[2])
        if username not in self._dict: return 0
        if entity_id not in self._dict[username]: return 0
        if criterion_id not in self._dict[username][entity_id]: return 0
        return self._dict[username][entity_id][criterion_id]
    
    def __setitem__(self, args: tuple[Union[str, "User"], Union[str, "Entity"], str], voting_right: float) -> None:
        username, entity_id, criterion_id = str(args[0]), str(args[1]), str(args[2])
        if username not in self._dict: self._dict[username] = dict()
        if entity_id not in self._dict[username]: self._dict[username][entity_id] = dict()
        self._dict[username][entity_id][criterion_id] = voting_right

    @classmethod
    def load(cls, filename: str) -> "VotingRights":
        return cls(pd.read_csv(filename, keep_default_na=False))
    
    def to_df(self) -> DataFrame:
        return DataFrame([
            Series({
                "username": username,
                "entity_id": entity_id,
                "criterion_id": criterion,
                "voting_right": voting_right
            })
            for username in self._dict
            for entity_id in self._dict[username]
            for criterion, voting_right in self._dict[username][entity_id].items()
        ])

    def save(self, directory: Union[str, Path]) -> tuple[str, dict]:
        path = Path(directory) / "voting_rights.csv"
        self.to_df().to_csv(path, index=False)
        return type(self).__name__, str(path)
        
    def __repr__(self) -> str:
        return repr(self.to_df()) 
