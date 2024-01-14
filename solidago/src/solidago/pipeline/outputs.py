from abc import ABC, abstractmethod
from typing import Literal

import pandas as pd

class PipelineOutput(ABC):
    @abstractmethod
    def save_individual_scalings(self, scalings: pd.DataFrame, criterion: str):
        """
        `scalings`: DataFrame with
            * index:  `user_id`  
            * columns: `s`, `delta_s`, `tau`, `delta_tau`
        """
        raise NotImplementedError
    
    @abstractmethod
    def save_individual_scores(self, scores: pd.DataFrame, criterion: str):
        """
        `scores`: DataFrame with columns
            * `user_id`
            * `entity_id`
            * `criteria`
            * `raw_score`
            * `raw_uncertainty`
            * `voting_right`
        """
        raise NotImplementedError

    @abstractmethod
    def save_entity_scores(
        self,
        scores: pd.DataFrame,
        criterion: str,
        score_mode: Literal["default", "all_equal", "trusted_only"]
    ):
        """
        scores: DataFrame with columns
            * `entity_id`
            * `criteria`
            * `score`
            * `uncertainty`
        """
        raise NotImplementedError
