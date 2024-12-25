from typing import Union
from pathlib import Path
from pandas import DataFrame, Series

import pandas as pd


class Criterion(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.name = str(self.name)

    @property
    def id(self) -> str:
        return str(self.name)
    
    @id.setter
    def id(self, criterion_id) -> None:
        self.name = str(criterion_id)
    
    def __hash__(self) -> int:
        return hash(self.id)
    
    def __str__(self) -> str:
        return str(self.name)


class Criteria(DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "criterion_id" in self.columns:
            self.set_index("criterion_id", inplace=True)
        else:
            self.index.name = "criterion_id"

    @classmethod
    def load(cls, filename: str) -> "Criteria":
        return cls(pd.read_csv(filename, keep_default_na=False))

    def save(self, directory) -> tuple[str, str]:
        path = Path(directory) / "criteria.csv"
        self.to_csv(path)
        return type(self).__name__, str(path)

    def get(self, criterion: Union[str, Criterion]) -> Criterion:
        return Criterion(self.loc[str(criterion)])
        
    def __iter__(self):
        iterator = self.iterrows()
        while True:
            try: yield next(iterator)
            except StopIteration: break
    
    def __repr__(self) -> str:
        return repr(DataFrame(self))
    
    def __contains__(self, criterion: Union[str, Series]) -> bool:
        return str(criterion) in set(self.index)
