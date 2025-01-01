from typing import Mapping, Optional, Union
from pathlib import Path

import numpy as np
import pandas as pd
import logging
import timeit

logger = logging.getLogger(__name__)

from solidago.state import State
from .sequential import Sequential
from .identity import Identity
from .trust_propagation import TrustPropagation
from .voting_right import VotingRights
from .preference_learning import PreferenceLearning
from .scaling import Scaling
from .aggregation import Aggregation
from .post_process import PostProcess


class Pipeline(Sequential):    
    def __init__(self,
        trust_propagation: TrustPropagation=TrustPropagation(),
        voting_rights_assignment: VotingRightsAssignment=VotingRightsAssignment(),
        preference_learning: PreferenceLearning=PreferenceLearning(),
        scaling: Scaling=Scaling(),
        aggregation: Aggregation=Aggregation(),
        post_process: PostProcess=PostProcess(),
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
        self.trust_propagation = trust_propagation
        self.voting_rights_assignment = voting_rights_assignment
        self.preference_learning = preference_learning
        self.scaling = scaling
        self.aggregation = aggregation
        self.post_process = post_process
