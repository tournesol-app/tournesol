from typing import Optional, Union

import numpy as np
import pandas as pd
import logging
import json

from solidago._state import *
from solidago._pipeline import Sequential

from ._user import UserGenerator
from ._vouch import VouchGenerator
from ._entity import EntityGenerator
from ._engagement import EngagementGenerator
from ._assessment import AssessmentGenerator
from ._comparison import ComparisonGenerator

logger = logging.getLogger(__name__)


class GenerativeModel(Sequential):
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
        super().__init__(
            user_gen = user_gen,
            entity_gen = entity_gen,
            vouch_gen = vouch_gen,
            engagement_gen = engagement_gen,
            assessment_gen = assessment_gen,
            comparison_gen = comparison_gen,
        )
 
    def __call__(self, state: Optional[State]=None, seed: Optional[int]=None) -> State:
        """ Generates a random dataset, presented as a state.
        No processing of the dataset is performed by the generative model.
        
        Parameters
        ----------
        state: State or None
            Optional state to derive computations from
        random_seed: None or int
            If int, sets numpy seed for reproducibility
            
        Returns
        -------
        state: State
        """
        if seed is not None:
            assert type(seed) == int
            np.random.seed(seed)
        
        if state is None:
            state = State()
        
        return super().__call__(state)

    @classmethod
    def load(cls, d: Union[dict, str]) -> "GenerativeModel":
        if isinstance(d, str):
            with open(d) as f:
                d = json.load(d)
        import solidago._generative_model as gen
        return cls(**{ key: getattr(gen, d[key][0])(**d[key][1]) for key in d })
       
