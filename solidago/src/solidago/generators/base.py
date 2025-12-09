from typing import Optional, Union

import numpy as np
import logging
import yaml

from solidago.poll import *
from solidago.modules import PollFunction, Sequential

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
        super().__init__([user, entity, vouch, engagement, assessment, comparison])
 
    def __call__(self, poll: Poll | None=None, seed: Optional[int]=None) -> Poll:
        """ Generates a random dataset, presented as a poll.
        No processing of the dataset is performed by the generative model.
        
        Parameters
        ----------
        poll: Poll or None
            Optional poll to derive computations from
        random_seed: None or int
            If int, sets numpy seed for reproducibility
            
        Returns
        -------
        poll: Poll
        """
        if seed is not None:
            assert type(seed) == int
            np.random.seed(seed)
        
        if poll is None:
            poll = Poll()
        
        return super().__call__(poll)

    @classmethod
    def load(cls, d: Union[dict, str]) -> "Generator":
        if isinstance(d, str):
            with open(d) as f:
                d = yaml.safe_load(f)
        return cls(**{ key: cls.load_generator(key, d[key][0], d[key][1]) for key in d })
    
    @classmethod
    def load_generator(cls, key: str, cls_name: str, kwargs: dict) -> PollFunction:
        import solidago.generators as generators
        return getattr(getattr(generators, key), cls_name)(**kwargs)
        
