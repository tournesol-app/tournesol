from abc import ABC, abstractmethod
from typing import Literal

import pandas as pd

class PipelineOutput(ABC):
    @abstractmethod
    def save_trust_scores(self, trusts: pd.DataFrame):
        """
        `trusts`: DataFrame with
            * index:  `user_id`  
            * columns: `trust_score`
        """
        raise NotImplementedError

    @abstractmethod
    def save_individual_scalings(self, scalings: pd.DataFrame):
        """
        `scalings`: DataFrame with
            * index:  `user_id`  
            * columns: `s`, `delta_s`, `tau`, `delta_tau`
        """
        raise NotImplementedError

    @abstractmethod
    def save_individual_scores(self, scores: pd.DataFrame):
        """
        `scores`: DataFrame with columns
            * `user_id`
            * `entity_id`
            * `raw_score`
            * `raw_uncertainty`
            * `voting_right`
        """
        raise NotImplementedError

    @abstractmethod
    def save_entity_scores(
        self,
        scores: pd.DataFrame,
        score_mode: Literal["default", "all_equal", "trusted_only"] = "default"
    ):
        """
        scores: DataFrame with columns
            * `entity_id`
            * `score`
            * `uncertainty`
        """
        raise NotImplementedError



class PipelineOutputInMemory(PipelineOutput):
    trust_scores: pd.DataFrame
    individual_scalings: pd.DataFrame
    individual_scores: pd.DataFrame
    entity_scores: pd.DataFrame

    def save_trust_scores(self, trusts: pd.DataFrame):
        self.trust_scores = trusts

    def save_individual_scalings(self, scalings):
        self.individual_scalings = scalings

    def save_entity_scores(self, scores, score_mode="default"):
        if score_mode != "default":
            return
        self.entity_scores = scores

    def save_individual_scores(self, scores):
        self.individual_scores = scores
