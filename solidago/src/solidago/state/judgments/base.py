from abc import ABC, abstractmethod
from typing import Optional, Union
from pathlib import Path
from pandas import DataFrame

import pandas as pd


class Assessments(DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self.columns) == 0:
            for column in ("username", "entity_id", "assessment", "assessment_min", "assessment_max"):
                self[column] = None

    def from_dict(d):
        return Assessments(DataFrame.from_dict(d))
    
    def extract_user(self, user: int):
        return Assessments(self[self["user_id"] == user])


class Comparisons(DataFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if len(self.columns) == 0:
            for column in ("username", "left_id", "right_id", "comparison", "comparison_max"):
                self[column] = None

    def from_dict(d):
        return Comparisons(DataFrame.from_dict(d))
    
    def extract_user(self, user: int):
        return Comparisons(self[self["user_id"] == user])
        

class Judgments:
    def __init__(
        self, 
        assessments: Assessments = Assessments(),
        comparisons: Comparisons = Comparisons(),
    ):
        """ Instantiates judgments from all contributors, based on dataframes """
        self._assessments = assessments
        self._comparisons = comparisons

    @classmethod
    def load(cls, filenames: dict[str, tuple[str, str]]):
        
        kwargs = dict()
        import solidago.state.judgments as judgments
        
        for key in filenames:
            subcls, filename = filenames[key]
            kwargs[key] = getattr(judgments, subcls)(pd.read_csv(filename))
        
        return cls(**kwargs)

    def save(self, directory) -> Union[str, list, dict]:
        filenames = dict()
        
        for key in ("comparisons", "assessments"):
            if len(getattr(self, key)) > 0:
                filename = Path(directory) / f"{key}.csv"
                getattr(self, key).to_csv(filename)
                filenames[key] = (getattr(self, key).__class__.__name__, str(filename))

        return type(self).__name__, filenames
    
    @property
    def assessments(self):
        return self._assessments
    
    @assessments.setter
    def assessments(self, value):
        self._assessments = value
    
    @property
    def comparisons(self):
        return self._comparisons
    
    @comparisons.setter
    def comparisons(self, value):
        self._comparisons = value
        
    def __getitem__(self, user: int) -> "Judgments":
        return Judgments(self.comparisons.extract_user(user), self.assessments.extract_user(user))

    def __repr__(self) -> str:
        return repr(self.assessments) + "\n\n" + repr(self.comparisons)
