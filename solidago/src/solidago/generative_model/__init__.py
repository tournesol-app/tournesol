from abc import ABC
from typing import Optional
from functools import cached_property

import numpy as np
import pandas as pd

from solidago.pipeline.inputs import TournesolInput

from .user_model import UserModel, SvdUserModel
from .vouch_model import VouchModel, ErdosRenyiVouchModel
from .entity_model import EntityModel, SvdEntityModel
from .true_score_model import TrueScoreModel, SvdTrueScoreModel
from .engagement_model import EngagementModel, SimpleEngagementModel
from .comparison_model import ComparisonModel, KnaryGBT

class SyntheticData(TournesolInput):
    def __init__(
        self, 
        users: pd.DataFrame = None,
        vouches: pd.DataFrame = None,
        entities: pd.DataFrame = None,
        true_scores: pd.DataFrame = None,
        comparisons: pd.DataFrame = None
    ):
        def df(**kwargs):
            dtypes = [(key, kwargs[key]) for key in kwargs]
            return pd.DataFrame(np.empty(0, np.dtype(list(dtypes))))
            
        self.users = users if users is not None else df(
            user_id=int, public_username=str, trust_score= float
        ).set_index("user_id")
        self.vouches = vouches if vouches is not None else df(
            voucher=int, vouchee=int, vouch=float
        )
        self.entities = entities
        self.true_scores = true_scores
        self.comparisons = comparisons if comparisons is not None else df(
            user_id=int, score=float, week_date=str, entity_a=int, entity_b=int
        )
 
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


class GenerativeModel:
    def __init__(
        self,
        user_model: UserModel = SvdUserModel(),
        vouch_model: VouchModel = ErdosRenyiVouchModel(),
        entity_model: EntityModel = SvdEntityModel(),
        true_score_model: TrueScoreModel = SvdTrueScoreModel(),
        engagement_model: EngagementModel = SimpleEngagementModel(),
        comparison_model: ComparisonModel = KnaryGBT(21, 10)
    ):
        """ Generate a random dataset
        Inputs:
        - user_model is a callable generator of users
        - vouch_model is a callable generator of vouches
        - entity_model is a callable generator of entities
        - true_score_model is a callable generator of true scores
        - comparison_model is a callable generator of comparisons
        - random_seed (if int) allows reproducibility
        """
        self.user_model = user_model
        self.vouch_model = vouch_model
        self.entity_model = entity_model
        self.true_score_model = true_score_model
        self.engagement_model = engagement_model
        self.comparison_model = comparison_model
 
    def __call__(
        self, n_users: int, n_entities: int, 
        random_seed: Optional[int] = None
    ) -> SyntheticData:
        """ Generates a random dataset
        Inputs:
        - n_users
        - n_entities
        - random_seed (if int) allows reproducibility
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        users = self.user_model(n_users)
        vouches = self.vouch_model(users)
        entities = self.entity_model(n_entities)
        true_scores = self.true_score_model(users, entities)
        comparisons = self.engagement_model(users, true_scores)
        comparisons = self.comparison_model(true_scores, comparisons)
        return SyntheticData(users, vouches, entities, true_scores, comparisons)


