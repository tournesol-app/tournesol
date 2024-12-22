from typing import Optional, Union
from pathlib import Path

import pandas as pd


class VotingRights(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for column in ("username", "entity_id", "criterion", "voting_right", "public"):
            if column not in self.columns:
                assert len(self) == 0
                self[column] = list()
    
    @classmethod
    def load(cls, filename: str):
        return cls(pd.read_csv(filename, keep_default_na=False))

    def save(self, directory: Union[str, Path]) -> Union[str, list, dict]:
        path = Path(directory) / "voting_rights.csv"
        self.to_csv(path)
        return str(path)

    def __call__(self, user: "User", entity: "Entity", criterion: str) -> float:
        """ self(user, entity, criterion) returns a voting right """
        df = self[(self["username"] == user.name) & (self["entity_id"] == entity.id) & (self["criterion"] == criterion)]
        if len(df) == 0:
            return 0
        return df[-1]["voting_right"]
        
    def is_public(self, user: "User", entity: "Entity", criterion: str) -> float:
        """ self(user, entity, criterion) returns a voting right """
        df = self[(self["username"] == user.name) & (self["entity_id"] == entity.id) & (self["criterion"] == criterion)]
        if len(df) == 0:
            return 0
        return df[-1]["public"]
    
    def set(self, user: "User", entity: "Entity", criterion: str, voting_right: float, privacy: Optional[bool]):
        """ sets the voting right of a user for an entity on a criterion """
        df = self[(self["username"] == user.name) & (self["entity_id"] == entity.id) & (self["criterion"] == criterion)]
        self.drop(df.index, inplace=True)
        self.loc[-1] = {
            "username": user.name,
            "entity_id": entity.id,
            "criterion": criterion,
            "voting_right": value
        }
        
    def __repr__(self):
        return repr(pd.DataFrame(self))        
