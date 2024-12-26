from typing import Optional, Union

import numpy as np
import pandas as pd
import logging
import json

from solidago.state import *

from .user import UserGenerator
from .vouch import VouchGenerator
from .entity import EntityGenerator
from .criterion import CriterionGenerator
from .engagement import EngagementGenerator
from .assessment import AssessmentGenerator
from .comparison import ComparisonGenerator

logger = logging.getLogger(__name__)


class GenerativeModel:
    def __init__(
        self,
        user_gen: UserGenerator = UserGenerator(),
        vouch_gen: VouchGenerator = VouchGenerator(),
        entity_gen: EntityGenerator = EntityGenerator(),
        criterion_gen: CriterionGenerator = CriterionGenerator(),
        engagement_gen: EngagementGenerator = EngagementGenerator(),
        assessment_gen: AssessmentGenerator = AssessmentGenerator(),
        comparison_gen: ComparisonGenerator = ComparisonGenerator(),
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
        self.user_gen = user_gen
        self.vouch_gen = vouch_gen
        self.entity_gen = entity_gen
        self.criterion_gen = criterion_gen
        self.engagement_gen = engagement_gen
        self.assessment_gen = assessment_gen
        self.comparison_gen = comparison_gen
 
    def __call__(self, n_users: int, n_entities: int, n_criteria: int=1, random_seed: Optional[int]=None) -> State:
        """ Generates a random dataset, presented as a state.
        No processing of the dataset is performed by the generative model.
        
        Parameters
        ----------
        n_users: int
            Number of users to generate
        n_entities: int
            Number of entities to generate
        n_criteria: int
            Number of criteria to generate
        random_seed: None or int
            If int, sets numpy seed for reproducibility
            
        Returns
        -------
        state: State
        """
        if random_seed is not None:
            assert type(random_seed) == int
            np.random.seed(random_seed)
        
        logger.info(f"Generate {n_users} users using {self.comparison_gen}")
        users = self.user_gen(n_users)
        logger.info(f"Generate vouches using {self.vouch_gen}")
        vouches = self.vouch_gen(users)
        logger.info(f"Generate {n_entities} entities using {self.entity_gen}")
        entities = self.entity_gen(n_entities)
        logger.info(f"Generate {n_criteria} criteria using {self.criterion_gen}")
        criteria = self.criterion_gen(n_criteria)
        logger.info(f"Generate user engagement using {self.engagement_gen}")
        made_public, judgments = self.engagement_gen(users, entities, criteria)
        logger.info(f"Generate assessments using {self.assessment_gen}")
        judgments.assessments = self.assessment_gen(users, entities, criteria, made_public, judgments)
        logger.info(f"Generate comparisons using {self.comparison_gen}")
        judgments.comparisons = self.comparison_gen(users, entities, criteria, made_public, judgments)
        
        return State(users, vouches, entities, criteria, made_public, judgments)

    @classmethod
    def load(cls, d: Union[dict, str]) -> "GenerativeModel":
        if isinstance(d, str):
            with open(d) as f:
                d = json.load(d)
        import solidago.generative_model as gen
        return cls(**{ key: getattr(gen, d[key][0])(**d[key][1]) for key in d })
        
    def to_json(self):
        return { key: getattr(self, key).to_json() for key in self.__dict__.keys() }
