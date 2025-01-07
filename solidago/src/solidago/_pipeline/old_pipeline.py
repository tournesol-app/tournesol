from typing import Mapping, Optional, Union
from pathlib import Path

import numpy as np
import pandas as pd
import logging
import timeit

logger = logging.getLogger(__name__)

from solidago.state import State
from .base import StateFunction
from .sequential import Sequential
from .identity import Identity


class Pipeline(Sequential):    
    def __init__(self,
        trust_propagation: StateFunction=Identity(),
        voting_rights_assignment: StateFunction=Identity(),
        preference_learning: StateFunction=Identity(),
        scaling: StateFunction=Identity(),
        aggregation: StateFunction=Identity(),
        post_process: StateFunction=Identity(),
    ):
        """Instantiates the pipeline components.
        
        Parameters
        ----------
        trust_propagation: TrustPropagation
            Algorithm to spread trust based on pretrusts and vouches
        voting_rights: VotingRights
            Algorithm to assign voting rights to each user
        preference_learning: PreferenceLearning
            Algorithm to learn a user model based on each user's data
        scaling: Scaling
            Algorithm to put user models on a common scale
        aggregation: Aggregation
            Algorithm to aggregate the different users' models
        post_process: PostProcess
            Algorithm to post-process user and global models,
            and make it readily usable for applications.
        """
        super().__init__(
            trust_propagation=trust_propagation,
            voting_rights_assignment=voting_rights_assignment,
            preference_learning=preference_learning,
            scaling=scaling,
            aggregation=aggregation,
            post_process=post_process,
        )

    @classmethod
    def load(cls, d: Union[dict, str]) -> "GenerativeModel":
        if isinstance(d, str):
            with open(d) as f:
                d = json.load(d)
        import solidago.pipeline as pipeline
        return cls(**{ key: getattr(pipeline, d[key][0])(**d[key][1]) for key in d })
    
