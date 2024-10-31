from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd

class Judgments(ABC):
    @abstractmethod
    def __getitem__(self, user: int) -> Optional[dict[str, pd.DataFrame]]:
        """ Returns user's judgments that can be used to infer a user model
        
        Parameters
        ----------
        user: int
        
        Returns
        -------
        out: dict[str, pd.DataFrame]
            judgments[u]["comparisons"] will typically yield a dataframe of comparisons
            Other entries may include "assessments"
        """
        raise NotImplementedError

class DataFrameJudgments(Judgments):
    def __init__(
        self, 
        comparisons: Optional[pd.DataFrame] = None,
        assessments: Optional[pd.DataFrame] = None,
    ):
        """ Instantiates judgments from all contributors, based on dataframes
        
        Parameters
        ----------
        comparisons: DataFrame with columns
            * `user_id`
            * `entity_a`
            * `entity_b`
            * `comparison`
            * `comparison_max`
        assessments: DataFrame with columns
            * `user_id`
            * `entity_id`
            * `assessment`
            * `assessment_type`
        """
        if comparisons is None:
            self.comparisons = pd.DataFrame(columns=[
                "user_id", "entity_a", "entity_b", "comparison", "comparison_max"
            ])
        else:
            self.comparisons = comparisons
            
        if assessments is None:
            self.assessments = pd.DataFrame(columns=[
                "user_id", "entity_id", "assessment", "assessment_type"
            ])
        else:
            self.assessments = assessments
        
    def __getitem__(self, user: int):
        comparisons = self.comparisons[self.comparisons["user_id"] == user]
        assessments = self.assessments[self.assessments["user_id"] == user]
        if len(comparisons) == 0 and len(assessments) == 0:
            return None
        return dict(
            comparisons=comparisons,
            assessments=assessments,
        )        
        

