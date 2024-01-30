from abc import ABC, abstractmethod

import pandas as pd

class Judgments(ABC):
    @abstractmethod
    def __getitem__(self, user: int) -> dict[str, pd.DataFrame]:
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
        comparisons: pd.DataFrame = None, 
        assessments: pd.DataFrame = None
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
        self.comparisons = comparisons
        if comparisons is None:
            self.comparisons = pd.DataFrame(columns=[
                "user_id", "entity_a", "entity_b", "comparison", "comparison_max"
            ])
            
        self.assessments = assessments
        if assessments is None:
            self.assessments = pd.DataFrame(columns=[
                "user_id", "entity_id", "assessment", "assessment_type"
            ])
        
    def __getitem__(self, user: int):
        return dict(
            comparisons=self.comparisons[self.comparisons["user_id"] == user],
            assessments=self.assessments[self.assessments["user_id"] == user]
        )        
        

