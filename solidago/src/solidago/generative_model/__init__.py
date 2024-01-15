from abc import ABC
from typing import Optional
from functools import cached_property

import numpy as np
import pandas as pd

from solidago.pipeline.inputs import TournesolInput
from .user_model import UserModel
from .vouch_model import VouchModel
from .entity_model import EntityModel
from .true_score_model import TrueScoreModel
from .comparison_model import ComparisonModel

class GenerativeModel(TournesolInput):
    def __init__(
        self,
        n_users: int,
        n_entities: int,
        user_model: UserModel,
        vouch_model: VouchModel,
        entity_model: EntityModel,
        true_score_model: TrueScoreModel,
        comparison_model: ComparisonModel,
        random_seed: Optional[int] = None,
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
        self.random_seed = random_seed
        if random_seed is not None:
            np.random.seed(random_seed)
        self.users = user_model(n_users)
        self.vouches = vouch_model(self.users)
        self.entities = entity_model(n_entities)
        self.true_scores = true_score_model(self.users, self.entities)
        self.comparisons = comparison_model(
            self.users, 
            self.entities, 
            self.true_scores
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



