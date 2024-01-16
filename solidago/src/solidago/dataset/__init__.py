from abc import ABC, abstractmethod
from typing import Optional
from functools import cached_property

import logging
import numpy as np
import pandas as pd

class Dataset(ABC):
    @abstractmethod
    def get_comparisons(
        self,
        criteria: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> pd.DataFrame:
        """Fetch data about comparisons submitted by users

        Returns:
        - comparisons_df: DataFrame with columns
            * `user_id`: int
            * `entity_a`: int or str
            * `entity_b`: int or str
            * `criteria`: str
            * `score`: float
            * `weight`: float
        """
        raise NotImplementedError

    @property
    @abstractmethod
    def ratings_properties(self) -> pd.DataFrame:
        """Fetch data about contributor ratings properties

        Returns:
        - ratings_df: DataFrame with columns
            * `user_id`: int
            * `entity_id`: int or str
            * `is_public`: bool
            * `is_scaling_calibration_user`: bool
            * `trust_score`: float
        """
        raise NotImplementedError

    @abstractmethod
    def get_individual_scores(
        self,
        criteria: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        raise NotImplementedError



class SimpleDataset(Dataset):
    def __init__(
        self, 
        users: pd.DataFrame = None,
        vouches: pd.DataFrame = None,
        entities: pd.DataFrame = None,
        true_scores: pd.DataFrame = None,
        user_scores: pd.DataFrame = None,
        comparisons: pd.DataFrame = None
    ):
        def df(x, **kwargs):
            if x is not None:
                return x
            dtypes = [(key, kwargs[key]) for key in kwargs]
            return pd.DataFrame(np.empty(0, np.dtype(list(dtypes))))
            
        self.users = df(users, user_id=int, public_username=str, trust_score= float)
        self.users.index.name = "user_id"
        self.vouches = df(vouches, voucher=int, vouchee=int, vouch=float)
        self.entities = entities
        self.true_scores = true_scores
        self.user_scores = df(user_scores, user_id=int, entity_id=int, is_public=bool)
        self.comparisons = df(comparisons, 
            user_id=int, score=float, week_date=str, entity_a=int, entity_b=int)
 
    def get_comparisons(
        self,
        criteria: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> pd.DataFrame:
        dtf = self.comparisons.copy(deep=False)
        if criteria is not None:
            dtf = dtf[dtf.criteria == criteria]
        if user_id is not None:
            dtf = dtf[dtf.user_id == user_id]
        dtf["weight"] = 1
        return dtf[["user_id", "entity_a", "entity_b", "criteria", "score", "weight"]]

    @cached_property
    def ratings_properties(self):
        user_entities_pairs = pd.Series(
            iter(
                set(self.comparisons.groupby(["user_id", "entity_a"]).indices.keys())
                | set(self.comparisons.groupby(["user_id", "entity_b"]).indices.keys())
            )
        )
        dtf = pd.DataFrame([*user_entities_pairs], columns=["user_id", "entity_id"])
        dtf["is_public"] = True
        dtf["trust_score"] = dtf["user_id"].map(self.users["trust_score"])
        scaling_calibration_user_ids = (
            dtf[dtf.trust_score > self.SCALING_CALIBRATION_MIN_TRUST_SCORE]["user_id"]
            .value_counts(sort=True)[: self.MAX_SCALING_CALIBRATION_USERS]
            .index
        )
        dtf["is_scaling_calibration_user"] = dtf["user_id"].isin(scaling_calibration_user_ids)
        return dtf

    def get_individual_scores(
        self,
        criteria: Optional[str] = None,
        user_id: Optional[int] = None,
    ) -> Optional[pd.DataFrame]:
        raise NotImplementedError

