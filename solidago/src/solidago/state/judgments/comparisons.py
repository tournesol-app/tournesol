from typing import Optional, Union
from pathlib import Path
from pandas import Series, DataFrame

import pandas as pd


class Comparison(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __hash__(self) -> int:
        return hash(self["username"] + self["left_id"] +  self["right_id"] + self["criterion_id"])


class Comparisons(DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get(self, 
        args: Union[
            Union[str, "Entity"],
            tuple[Union[str, "Entity"], Union[str, "Entity"]]
        ]
    ) -> Union[dict[str, Comparison], Comparison]:
        from solidago.state import Entity
        if isinstance(args, (str, Entity)):
            df_left = self[(self["left_id"] == str(args))]
            df_right = self[(self["right_id"] == str(args))]
            return {
                "as_left": { r["right_id"]: Comparison(r) for _, r in df_left.iterrows() },
                "as_right": { r["left_id"]: Comparison(r) for _, r in df_right.iterrows() }
            }
        left, right = str(args[0]), str(args[1])
        df = self[(self["left_id"] == left) & (self["right_id"] == right)]
        return Comparison(df.iloc[-1]) if len(df) > 0 else None
    
    def __iter__(self):
        for _, row in self.iterrows():
            yield Comparison(row)
    
    def __repr__(self):
        return repr(DataFrame(self))
    

class ComparisonsDictionary:
    def __init__(self, d: Optional[Union[dict, DataFrame]]=None):
        self._dict = d if isinstance(d, dict) else dict()
        if isinstance(d, DataFrame):
            for _, r in d.iterrows():
                username, criterion_id = r["username"], r["criterion_id"]
                del r["username"], r["criterion_id"]
                if username not in self._dict:
                    self._dict[username] = dict()
                if criterion_id not in self._dict[username]:
                    self._dict[username][criterion_id] = list()
                self._dict[username][criterion_id].append(r)
            for username in self._dict:
                for criterion_id in self._dict[username]:
                    self._dict[username][criterion_id] = Comparisons(self._dict[username][criterion_id])

    @classmethod
    def load(cls, filename: str) -> "ComparisonsDictionary":
        try: return cls(pd.read_csv(filename, keep_default_na=False, dtype={ 
            "username": str, "criterion_id": str, "left_id": str, "right_id": str
        }))
        except pd.errors.EmptyDataError: return cls()
    
    def __len__(self) -> int:
        return sum([
            len(self._dict[username][criterion_id])
            for username in self._dict
            for criterion_id in self._dict[username]
        ])
    
    def to_df(self) -> DataFrame:
        rows = list()
        for username in self._dict:
            for criterion_id in self._dict[username]:
                df = self._dict[username][criterion_id]
                df["username"] = username
                df["criterion_id"] = criterion_id
                rows += [row for _, row in df.iterrows()]
        return DataFrame(rows)

    def save(self, directory: Union[str, Path]) -> tuple[str, dict[str, str]]:
        filename = Path(directory) / "comparisons.csv"
        self.to_df().to_csv(filename, index=False)
        return type(self).__name__, str(filename)
    
    def __getitem__(self, 
        args: Union[
            tuple[Union[str, "User"], Union[str, "Criterion"], Union[str, "Entity"], Union[str, "Entity"]],
            tuple[Union[str, "User"], Union[str, "Criterion"], Union[str, "Entity"]],
            tuple[Union[str, "User"], Union[str, "Criterion"]],
            Union[str, "User"]
        ]
    ) -> Union[Optional[Comparison], Comparisons, dict[str, Comparisons]]:
        from solidago.state import User
        if isinstance(args, (str, User)):
            return self._dict[str(args)]
        username, criterion_id = str(args[0]), str(args[1])
        if username not in self._dict or criterion_id not in self._dict[username] and len(args) == 2:
            return Comparisons()
        if len(args) == 2:
            return self._dict[username][criterion_id]
        args2 = args[2] if len(args) == 3 else args[2:]
        return self._dict[username][criterion_id].get(args2)

    def __iter__(self):
        for username in self._dict:
            for criterion_id in self._dict[username]:
                yield username, criterion_id, self[username][criterion_id]

    def __repr__(self):
        return repr(self.to_df())
