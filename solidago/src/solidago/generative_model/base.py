from typing import Optional, Union

import numpy as np
import pandas as pd
import logging
import json

from solidago.state import *
from solidago.pipeline import Sequential

from .user import UserGenerator
from .vouch import VouchGenerator
from .entity import EntityGenerator
from .engagement import EngagementGenerator
from .assessment import AssessmentGenerator
from .comparison import ComparisonGenerator

logger = logging.getLogger(__name__)


class GenerativeModel(Sequential):
    module_names = ("user_gen", "vouch_gen", "entity_gen", 
        "engagement_gen", "assessment_gen", "comparison_gen")

    def __init__(self,
        user_gen: UserGenerator = UserGenerator(),
        entity_gen: EntityGenerator = EntityGenerator(),
        vouch_gen: VouchGenerator = VouchGenerator(),
        engagement_gen: EngagementGenerator = EngagementGenerator(),
        assessment_gen: AssessmentGenerator = AssessmentGenerator(),
        comparison_gen: ComparisonGenerator = ComparisonGenerator(),
    ):
        """ Pipeline to generate a random dataset
        
        Parameters
        ----------
        user_model: UserModel
            Generates users
        entity_model: EntityModel
            Generates entities
        vouch_model: VouchModel
            Generates vouches
        engagement_model: EngagementModel
            Generates private/public selection, and comparisons to be made
        assessment_model: AssessmentModel
            Generates assessment values
        comparison_model: ComparisonModel
            Generates comparisons values
        """
        super().__init__(user_gen, entity_gen, vouch_gen, engagement_gen,
            assessment_gen, comparison_gen)
 
    def __call__(self, random_seed: Optional[int]=None) -> State:
        """ Generates a random dataset, presented as a state.
        No processing of the dataset is performed by the generative model.
        
        Parameters
        ----------
        random_seed: None or int
            If int, sets numpy seed for reproducibility
            
        Returns
        -------
        state: State
        """
        if random_seed is not None:
            assert type(random_seed) == int
            np.random.seed(random_seed)
        
        state = State()
        for name, module in zip(self.module_names, self.modules):
            logger.info(f"Running {name} with {type(module).__name__}")
            module(state)
            
        return state

    @classmethod
    def load(cls, d: Union[dict, str]) -> "GenerativeModel":
        if isinstance(d, str):
            with open(d) as f:
                d = json.load(d)
        import solidago.generative_model as gen
        return cls(**{ key: getattr(gen, d[key][0])(**d[key][1]) for key in d })
        
    def to_json(self):
        return type(self).__name__, { m: getattr(self, m).to_json() for key in self.module_names }

