from typing import Union, Optional
from pathlib import Path
from pandas import DataFrame, Series

import pandas as pd


class Vouches:
    def __init__(self, d: Optional[Union[dict, DataFrame]]=None):
        self._dict = d if isinstance(d, dict) else dict()
        if isinstance(d, DataFrame):
            if "priority" not in d.columns:
                d["priority"] = 0
            for _, r in d.iterrows():
                self[r["by"], r["to"], r["kind"]] = r["weight"], r["priority"]
    
    def __getitem__(self, 
        args: Union[
            Union[str, "User"],
            tuple[Union[str, "User"], Union[str, "User"]], 
            tuple[Union[str, "User"], Union[str, "User"], str]
        ]
    ) -> Union[dict[str, dict[str, tuple[float, float]]], tuple[float, float]]:
        """ If a voucher and vouchee are given in inputs, returns (weight, priority) of the vouch.
        If only a voucher is given in inputs, 
        returns a dict d such that d[kind][vouchee_id] yields self[kind][voucher_id][vouchee_id]. 
        """
        from solidago.state.users import User
        if isinstance(args, (str, User)):
            return {
                kind: { vouchee_id: vouch for vouchee_id, vouch in self._dict[kind][str(args)].items() }
                for kind in self._dict
            }
        voucher_id, vouchee_id = str(args[0]), str(args[1])
        kind = args[2] if len(args) > 2 else "ProofOfPersonhood"
        if kind not in self._dict: return 0
        if voucher_id not in self._dict[kind]: return 0
        if vouchee_id not in self._dict[kind][voucher_id]: return 0
        return self._dict[kind][voucher_id][vouchee_id]
    
    def __setitem__(self, 
        args: Union[
            tuple[Union[str, "User"], Union[str, "User"]], 
            tuple[Union[str, "User"], Union[str, "User"], str]
        ],
        vouch: Union[float, tuple[float, float]]
    ) -> None:
        vouch = (vouch, 0) if isinstance(vouch, (float, int)) else vouch
        assert vouch[0] >= 0
        voucher_id, vouchee_id = str(args[0]), str(args[1])
        kind = args[2] if len(args) > 2 else "ProofOfPersonhood"
        if kind not in self._dict: self._dict[kind] = dict()
        if voucher_id not in self._dict[kind]: self._dict[kind][voucher_id] = dict()
        self._dict[kind][voucher_id][vouchee_id] = vouch

    @classmethod
    def load(cls, filename: str) -> "Vouches":
        return cls(pd.read_csv(filename, keep_default_na=False))

    def to_df(self) -> DataFrame:
        return DataFrame([
            [ kind, voucher_id, vouchee_id, out[0], out[1] ]
            for kind in self._dict
            for voucher_id in self._dict[kind]
            for vouchee_id, out in self._dict[kind][voucher_id].items()
        ], columns=["kind", "by", "to", "weight", "priority"])

    def save(self, directory: Union[str, Path]) -> tuple[str, str]:
        path = Path(directory) / "vouches.csv"
        self.to_df().to_csv(path)
        return type(self).__name__, str(path)

    def __repr__(self) -> str:
        return repr(self.to_df()) 
