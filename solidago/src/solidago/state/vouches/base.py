from typing import Union, Optional
from pathlib import Path

import pandas as pd


class Vouches:
    def __init__(self, d: Union[dict, pd.DataFrame]=dict()):
        self._dict = d if isinstance(d, dict) else dict()
        if isinstance(d, pd.DataFrame):
            if "priority" not in d.columns:
                d["priority"] = 0
            for _, r in d.iterrows():
                self[r["by"], r["to"], r["kind"]] = r["weight"], r["priority"]
    
    def __getitem__(self, args: tuple[Union[str, "User"], Union[str, "User"], str]) -> tuple[float, float]:
        """ Returns (weight, priority) of the vouch """
        voucher = args[0] if isinstance(args[0], str) else args[0].name
        vouchee = args[1] if isinstance(args[1], str) else args[1].name
        kind = args[2] if len(args) > 2 else "ProofOfPersonhood"
        if kind not in self._dict: return 0
        if voucher not in self._dict[kind]: return 0
        if vouchee not in self._dict[kind][voucher]: return 0
        return self._dict[kind][voucher][vouchee]
    
    def __setitem__(self, args: tuple[Union[str, "User"], Union[str, "User"], str], vouch: Union[float, tuple[float, float]]):
        vouch = (vouch, 0) if isinstance(vouch, (float, int)) else vouch
        assert vouch[0] >= 0
        voucher = args[0] if isinstance(args[0], str) else args[0].name
        vouchee = args[1] if isinstance(args[1], str) else args[1].name
        kind = args[2] if len(args) > 2 else "ProofOfPersonhood"
        if kind not in self._dict: self._dict[kind] = dict()
        if voucher not in self._dict[kind]: self._dict[kind][voucher] = dict()
        self._dict[kind][voucher][vouchee] = vouch

    @classmethod
    def load(cls, filename: str) -> "Vouches":
        return cls(pd.read_csv(filename, keep_default_na=False))

    def to_df(self):
        return pd.DataFrame([
            pd.Series({ "kind": kind, "by": voucher, "to": vouchee, "weight": out[0], "priority": out[1] })
            for kind in self._dict
            for voucher in self._dict[kind]
            for vouchee, out in self._dict[kind][voucher].items()
        ])

    def save(self, directory: Union[str, Path]) -> Union[str, list, dict]:
        path = Path(directory) / "vouches.csv"
        self.to_df().to_csv(path)
        return str(path)

    def __repr__(self):
        return repr(self.to_df()) 
