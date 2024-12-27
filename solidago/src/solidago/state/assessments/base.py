from typing import Optional, Union
from pathlib import Path
from pandas import Series, DataFrame
from types import SimpleNamespace

import pandas as pd


class Assessment(Series):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def __hash__(self) -> int:
        return hash(self["username"] + self["entity_id"] + self["criterion_id"])


class UserCriterionAssessments(DataFrame):
    def __init__(self, 
        user: Optional[Union[str, "User"]], 
        criterion: Optional[Union[str, "Criterion"]], 
        *args, 
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.meta = SimpleNamespace()
        self.meta.username = str(user)
        self.meta.criterion_id = str(criterion) 
    
    @property
    def username(self) -> str:
        return self.meta.username
        
    @username.setter
    def username(self, user: Union[str, "User"]):
        self.meta.username = str(user)
        
    @property
    def criterion_id(self) -> str:
        return self.meta.criterion_id
        
    @criterion_id.setter
    def criterion_id(self, criterion: Union[str, "Criterion"]):
        self.meta.criterion_id = str(criterion)

    def get(self, entity: Union[str, "Entity"]) -> Optional[Assessment]:
        df = self[self["entity_id"] == str(entity)]
        return Assessment(df.iloc[-1]) if len(df) > 0 else None
    
    def __iter__(self):
        for _, row in self.iterrows():
            yield Assessment(row)
    
    def __repr__(self):
        return repr(DataFrame(self))
        

class Assessments:
    def __init__(self, d: Optional[Union[dict, DataFrame]]=None, *args, **kwargs):
        self._dict = d if isinstance(d, dict) else dict()
        if isinstance(d, dict):
            for username in d:
                for criterion_id in d[username]:
                    d[username][criterion_id] = UserCriterionAssessments(
                        username, 
                        criterion_id, 
                        d[username][criterion_id],
                        *args, 
                        **kwargs
                    )
        if isinstance(d, DataFrame):
            for _, r in d.iterrows():
                username, criterion_id = r["username"], r["criterion_id"]
                if username not in self._dict:
                    self._dict[username] = dict()
                if criterion_id not in self._dict[username]:
                    self._dict[username][criterion_id] = list()
                self._dict[username][criterion_id].append(r)
            for username in self._dict:
                for criterion_id in self._dict[username]:
                    self._dict[username][criterion_id] = UserCriterionAssessments(
                        username,
                        criterion_id,
                        self._dict[username][criterion_id],
                        *args, 
                        **kwargs
                    )

    @classmethod
    def load(cls, filename: str) -> "Assessments":
        try: return cls(pd.read_csv(filename, keep_default_na=False, dtype={ 
            "username": str, "criterion_id": str, "entity_id": str
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
        filename = Path(directory) / "assessments.csv"
        self.to_df().to_csv(filename, index=False)
        return type(self).__name__, str(filename)
    
    def __getitem__(self, 
        args: Union[
            tuple[Union[str, "User"], Union[str, "Criterion"], Union[str, "Entity"]],
            tuple[Union[str, "User"], Union[str, "Criterion"]],
            Union[str, "User"]
        ]
    ) -> Union[Optional[Assessment], UserCriterionAssessments, dict[str, UserCriterionAssessments]]:
        from solidago.state import User
        if isinstance(args, (str, User)):
            return self._dict[str(args)]
        username, criterion_id = str(args[0]), str(args[1])
        if username not in self._dict or criterion_id not in self._dict[username] and len(args) == 2:
            return Assessments()
        if len(args) == 2:
            return self._dict[username][criterion_id]
        return self._dict[username][criterion_id].get(str(args[2]))

    def __iter__(self):
        for username in self._dict:
            for criterion_id, assessments in self._dict[username].items():
                yield username, criterion_id, assessments

    def __repr__(self):
        return repr(self.to_df())

    def get_evaluators(self, entity: Union[str, "Entity"], criterion: Union[str, "Criterion"]) -> set[str]:
        """ Returns all usernames of users who assessed entity on criterion """
        return { 
            username for username in self._dict
            if self[username, criterion].get(entity) is not None
        }
    
