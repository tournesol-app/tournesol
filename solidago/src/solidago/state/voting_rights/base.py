from typing import Optional, Union
from pathlib import Path

import pandas as pd


class VotingRights(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    @classmethod
    def load(cls, filename: str):
        return cls(pd.read_csv(filename, keep_default_na=False))

    def save(self, directory: Union[str, Path]) -> Union[str, list, dict]:
        path = Path(directory) / "voting_rights.csv"
        self.to_csv(path)
        return str(path)

    def get(self, user) -> float:
        """ self[user, entity] must returns the voting right of a user for an entity
                
        Parameters
        ----------
        user_entity_tuple: (user: int, entity: int)
        
        Returns
        -------
        out: float
        """
        user, entity = user_entity_tuple
        if entity not in self._dict:
            return 0
        if user not in self._dict[entity]:
            return 0
        return self._dict[entity][user]
    
    def __setitem__(self, user_entity_tuple:tuple[int, int], value: float):
        """ sets the voting right of a user for an entity
                
        Parameters
        ----------
        user_entity_tuple: (user: int, entity: int)
        value: float
        """
        user, entity = user_entity_tuple
        if entity not in self._dict:
            self._dict[entity] = dict()
        self._dict[entity][user] = value

    def entities(self, user: Optional[int] = None) -> set[int]:
        if user is None:
            return set(self._dict.keys())
        return { e for e in self._dict if user in self._dict[e] }
        
    def on_entity(self, entity: int) -> dict[int, float]:
        return self._dict[entity]

    def to_dict(self):
        return self._dict

    def from_dict(d: dict):
        return VotingRights(d)

    def from_df(df):
        v = VotingRights()
        for _, row in df.iterrows():
            self
        
