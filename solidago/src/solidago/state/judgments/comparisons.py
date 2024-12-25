from typing import Optional, Union
from pathlib import Path
from pandas import Series, DataFrame

import pandas as pd


class Comparison(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class Comparisons(DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __iter__(self):
        for _, row in self.iterrows():
            yield Comparison(row)
    

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
        try: return cls(pd.read_csv(filename))
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
        user_criterion: Union[
            tuple[Union[str, "User"], Union[str, "Criterion"]],
            Union[str, "User"]
        ]
    ) -> Union["Comparisons", dict[str, "Comparisons"]]:
        from solidago.state import User
        if isinstance(user_criterion, (str, User)):
            return self._dict[str(user_criterion)]
        username, criterion_id = str(user_criterion[0]), str(user_criterion[1])
        if username not in self._dict or criterion_id not in self._dict[username]:
            return Comparisons()
        return self._dict[username][criterion_id]

    def __iter__(self):
        for username in self._dict:
            for criterion_id in self._dict[criterion_id]:
                yield username, criterion_id, self[username][criterion_id]
