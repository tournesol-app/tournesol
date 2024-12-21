from typing import Union, Optional
from pathlib import Path

import pandas as pd


class Vouches(pd.DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "kind" not in self.columns:
            self["kind"] = "ProofOfPersonhood"
        if "weight" not in self.columns:
            self["weight"] = 1
        if "priority" not in self.columns:
            self["priority"] = 0
        self.iterator = None

    @classmethod
    def load(cls, filename: str):
        return cls(pd.read_csv(filename))

    def save(self, directory: Union[str, Path]) -> Union[str, list, dict]:
        path = Path(directory) / "vouches.csv"
        self.to_csv(path)
        return str(path)
    
    def get(self, by: "User", to: Optional["User"]=None, kind: Optional[str]=None) -> Union[tuple[float, float], dict]:
        """ Return vouch or vouches, depending on input
        
        Returns
        -------
        out: dict[str, dict[User, tuple[float, float]]]
            if to is None and kind is None
        out: dict[User, tuple[float, float]]
            if to is None and kind: str
        out: dict[str, tuple[float, float]]
            if to: User and kind is None
        weight, priority: tuple[float, float]
            if to: User and kind: str
        """
        v = self[self["by_username"] == by.name]
        if kind is None:
            return { k: get(by, to, k) for k in set(v["kind"]) }
        v = self[v["kind"] == kind]
        if to is None:
            return { t: get(by, to, kind) for t in set(v["to"]) }
        v = v[v["to_username"] == to.name]
        return (0, - float("inf")) if len(v) == 0 else (v.iloc[-1]["weight"], v.iloc[-1]["priority"])

    def set(self, by: "User", to: "User", kind: str="ProofOfPersonhood", weight: float=1, priority: float=1):
        self.iloc[-1] = { "by": by.name, "to": to.name, "kind": kind, "weight": weight, "priority": priority }
            
    def __iter__(self):
        self.iterator = super(Vouches, self).iterrows()
        return self
    
    def __next__(self):
        _, vouch = next(self.iterator)
        return vouch
    
    def __repr__(self):
        return repr(pd.DataFrame(self))
    
