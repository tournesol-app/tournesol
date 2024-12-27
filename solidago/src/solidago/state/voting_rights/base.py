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
    
    def __getitem__(self, 
        args: Union[
            Union[str, "User"],
            tuple[Union[str, "User"], Union[str, "Entity"]],
            tuple[Union[str, "User"], Union[str, "Entity"], Union[str, "Criterion"]]
        ]
    ) -> Union[dict[str, dict[str, float]], dict[str, float], float]:
        from solidago.state import User, Entity
        if isinstance(args, (str, User)):
            return self._dict[str(args)] if str(args) in self._dict else dict()
        elif len(args) == 2:
            username, entity_id = str(args[0]), str(args[1])
            if username not in self._dict: return dict()
            return self._dict[username][entity_id] if entity_id in self._dict[username] else dict()
        username, entity_id, criterion_id = str(args[0]), str(args[1]), str(args[2])
        if username not in self._dict: return 0
        if entity_id not in self._dict[username]: return 0
        if criterion_id not in self._dict[username][entity_id]: return 0
        return self._dict[username][entity_id][criterion_id]
    
    def __setitem__(self, 
        args: tuple[Union[str, "User"], Union[str, "Entity"], Union[str, "Criterion"]], 
        voting_right: float
    ) -> None:
        username, entity_id, criterion_id = str(args[0]), str(args[1]), str(args[2])
        if username not in self._dict: self._dict[username] = dict()
        if entity_id not in self._dict[username]: self._dict[username][entity_id] = dict()
        self._dict[username][entity_id][criterion_id] = voting_right

    @classmethod
    def load(cls, filename: str) -> "VotingRights":
        try: return cls(pd.read_csv(filename, keep_default_na=False))
        except pd.errors.EmptyDataError: return cls()
    
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
