from abc import ABC
from typing import Optional
from functools import cached_property

import logging
import numpy as np
import pandas as pd

from solidago.dataset import SimpleDataset

from .user_model import UserModel, SvdUserModel
from .vouch_model import VouchModel, ErdosRenyiVouchModel
from .entity_model import EntityModel, SvdEntityModel
from .true_score_model import TrueScoreModel, SvdTrueScoreModel
from .engagement_model import EngagementModel, SimpleEngagementModel
from .comparison_model import ComparisonModel, KnaryGBT


logger = logging.getLogger(__name__)


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
    ) -> SimpleDataset:
        """ Generates a random dataset
        Inputs:
        - n_users
        - n_entities
        - random_seed (if int) allows reproducibility
        """
        if random_seed is not None:
            np.random.seed(random_seed)
        
        logger.info(f"Generate {n_users} users using {self.user_model}")
        users = self.user_model(n_users)
        logger.info(f"Generate vouches using {self.vouch_model}")
        vouches = self.vouch_model(users)
        logger.info(f"Generate {n_entities} entities using {self.entity_model}")
        entities = self.entity_model(n_entities)
        logger.info(f"Generate ground truth using {self.true_score_model}")
        true_scores = self.true_score_model(users, entities)
        logger.info(f"Generate user engagement using {self.engagement_model}")
        scores, comparisons = self.engagement_model(users, true_scores)
        logger.info(f"Generate comparisons using {self.comparison_model}")
        comparisons = self.comparison_model(true_scores, comparisons)
        return SimpleDataset(users, vouches, entities, true_scores, scores, comparisons)

