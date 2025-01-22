from typing import Optional, Union

import numpy as np
import pandas as pd
import logging
import json

from solidago.state import *
from solidago.modules import StateFunction, Sequential

from .user import UserGen
from .vouch import VouchGen
from .entity import EntityGen
from .engagement import EngagementGen
from .assessment import AssessmentGen
from .comparison import ComparisonGen

logger = logging.getLogger(__name__)


class Generator(Sequential):
    def __init__(self,
        user: UserGen = UserGen(),
        entity: EntityGen = EntityGen(),
        vouch: VouchGen = VouchGen(),
        engagement: EngagementGen = EngagementGen(),
        assessment: AssessmentGen = AssessmentGen(),
        comparison: ComparisonGen = ComparisonGen(),
    ):
        """ Pipeline to generate a random dataset """
        super().__init__(user=user, entity=entity, vouch=vouch, 
            engagement=engagement, assessment=assessment, comparison=comparison)
 
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
    def load(cls, d: Union[dict, str]) -> "Generator":
        if isinstance(d, str):
            with open(d) as f:
                d = json.load(f)
        return cls(**{ key: cls.load_generator(key, d[key][0], d[key][1]) for key in d })
    
    @classmethod
    def load_generator(cls, key: str, cls_name: str, kwargs: dict) -> StateFunction:
        import solidago.generators as generators
        return getattr(getattr(generators, key), cls_name)(**kwargs)
        
