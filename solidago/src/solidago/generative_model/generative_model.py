from typing import Optional

import logging
import numpy as np
import pandas as pd

from .user_model import UserModel, NormalUserModel
from .vouch_model import VouchModel, ErdosRenyiVouchModel
from .entity_model import EntityModel, NormalEntityModel
from .engagement_model import EngagementModel, SimpleEngagementModel
from .comparison_model import ComparisonModel, KnaryGBT

from solidago.privacy_settings import PrivacySettings
from solidago.judgments import DataFrameJudgments


logger = logging.getLogger(__name__)


class GenerativeModel:
    def __init__(
        self,
        user_model: UserModel = NormalUserModel(svd_dimension=5),
        vouch_model: VouchModel = ErdosRenyiVouchModel(),
        entity_model: EntityModel = NormalEntityModel(svd_dimension=5),
        engagement_model: EngagementModel = SimpleEngagementModel(),
        comparison_model: ComparisonModel = KnaryGBT(21, 10)
    ):
        """ Pipeline to generate a random dataset
        
        Parameters
        ----------
        user_model: UserModel
            Generates users
        vouch_model: VouchModel
            Generates vouches
        entity_model: EntityModel
            Generates entities
        engagement_model: EngagementModel
            Generates private/public selection, and comparisons to be made
        comparison_model: ComparisonModel
            Generates comparisons values, given comparisons to be made and true scores
        """
        self.user_model = user_model
        self.vouch_model = vouch_model
        self.entity_model = entity_model
        self.engagement_model = engagement_model
        self.comparison_model = comparison_model
 
    def __call__(
        self, n_users: int, n_entities: int, 
        random_seed: Optional[int] = None
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, PrivacySettings, DataFrameJudgments]:
        """ Generates a random dataset
        
        Parameters
        ----------
        n_users: int
            Number of users to generate
        n_entities: int
            Number of entities to generate
        random_seed: None or int
            If int, sets numpy seed for reproducibility
            
        Returns
        -------
        users: DataFrame with columns
            * user_id
        vouches: DataFrame with columns
            * voucher
            * vouchee
            * vouch
        entities: DataFrame with columns
            * entity_id
        privacy: PrivacySettings
            privacy[user, entity] in { True, False, None }
        judgments: DataFrameJudgments
            judgments[user]["comparisons"] is user's DataFrame with columns
                * entity_a
                * entity_b
                * comparison
                * comparison_max
        """
        if random_seed is not None:
            assert type(random_seed) == int
            np.random.seed(random_seed)
        
        logger.info(f"Generate {n_users} users using {self.user_model}")
        users = self.user_model(n_users)
        logger.info(f"Generate vouches using {self.vouch_model}")
        vouches = self.vouch_model(users)
        logger.info(f"Generate {n_entities} entities using {self.entity_model}")
        entities = self.entity_model(n_entities)
        logger.info(f"Generate user engagement using {self.engagement_model}")
        privacy, judgments = self.engagement_model(users, entities)
        logger.info(f"Generate comparisons using {self.comparison_model}")

        # FIXME: `engagement_model` is of type `EngagementModel` which produces generic "Judgments",
        # but here we assume that Judgements can be assigned "comparisons"..
        # Does that mean "DataFrameJudgments" should be used instead?
        judgments.comparisons = self.comparison_model(users, entities, judgments.comparisons)
        return users, vouches, entities, privacy, judgments

    @classmethod
    def from_json(cls, json) -> "GenerativeModel":
        return GenerativeModel(
            user_model=user_model_from_json(json["user_model"]),
            vouch_model=vouch_model_from_json(json["vouch_model"]),
            entity_model=entity_model_from_json(json["entity_model"]),
            engagement_model=engagement_model_from_json(json["engagement_model"]),
            comparison_model=comparison_model_from_json(json["comparison_model"]),
        )
        
    def to_json(self):
        return dict(
            user_model=self.user_model.to_json(),
            vouch_model=self.vouch_model.to_json(),
            entity_model=self.entity_model.to_json(),
            engagement_model=self.engagement_model.to_json(),
            comparison_model=self.comparison_model.to_json()
        )
        

def user_model_from_json(json):
    if json[0] == "NormalUserModel": 
        return NormalUserModel(**json[1])
    raise ValueError(f"UserModel {json[0]} was not recognized")
    
def vouch_model_from_json(json):
    if json[0] == "ErdosRenyiVouchModel": 
        return ErdosRenyiVouchModel()
    raise ValueError(f"VouchModel {json[0]} was not recognized")
    
def entity_model_from_json(json):
    if json[0] == "NormalEntityModel": 
        return NormalEntityModel(**json[1])
    raise ValueError(f"EntityModel {json[0]} was not recognized")
    
def engagement_model_from_json(json):
    if json[0] == "SimpleEngagementModel": 
        return SimpleEngagementModel(**json[1])
    raise ValueError(f"EngagementModel {json[0]} was not recognized")
    
def comparison_model_from_json(json):
    if json[0] == "KnaryGBT": 
        return KnaryGBT(**json[1])
    raise ValueError(f"ComparisonModel {json[0]} was not recognized")
    



