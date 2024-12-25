from typing import Mapping, Optional, Union

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
    module_names = ("trust_propagation", "voting_rights_assignment", "preference_learning", 
        "scaling", "aggregation", "post_process")
    
    def __init__(self,
        trust_propagation: Union[TrustPropagation, Identity]=Identity(),
        voting_rights_assignment: Union[VotingRightsAssignment, Identity]=Identity(),
        preference_learning: Union[PreferenceLearning, Identity]=Identity(),
        scaling: Union[Scaling, Identity]=Identity(),
        aggregation: Union[Aggregation, Identity]=Identity(),
        post_process: Union[PostProcess, Identity]=Identity(),
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
        super().__init__(trust_propagation, voting_rights_assignment, preference_learning, 
            scaling, aggregation, post_process)

    @classmethod
    def from_json(cls, json) -> "Pipeline":
        import solidago.pipeline as pipeline
        return Pipeline(*[ getattr(pipeline, json[name][0])(**json[name][1]) for name in cls.module_names ])
                
    def to_json(self):
        return { name: getattr(self, name).to_json() for name in module_names }
        
    def __call__(self, state: State, save_directory: Optional[str]=None) -> State:
        state.save_directory = save_directory
        logger.info("Starting the full Solidago pipeline")
        start_step1 = timeit.default_timer()
    
        logger.info(f"Pipeline 1. Propagating trust with {str(self.trust_propagation)}")
        state = self.trust_propagation(state)
        start_step2 = timeit.default_timer()
        logger.info(f"Pipeline 1. Terminated in {np.round(start_step2 - start_step1, 2)} seconds")
        state.save_trust_scores()
            
        logger.info(f"Pipeline 2. Computing voting rights with {str(self.voting_rights)}")
        # WARNING: `privacy` may contain (user, entity) even if user has expressed no judgement
        # about the entity. These users should not be given a voting right on the entity.
        # For now, irrelevant privacy values are excluded in `input.get_pipeline_kwargs()`
        state = self.voting_rights(state)
        start_step3 = timeit.default_timer()
        logger.info(f"Pipeline 2. Terminated in {np.round(start_step3 - start_step2, 2)} seconds")
        
        logger.info(f"Pipeline 3. Learning preferences with {str(self.preference_learning)}")
        state = self.preference_learning(state)
        start_step4 = timeit.default_timer()
        logger.info(f"Pipeline 3. Terminated in {int(start_step4 - start_step3)} seconds")
        state.save_user_direct_scores()
        
        logger.info(f"Pipeline 4. Collaborative scaling with {str(self.scaling)}")
        state = self.scaling(state)
        start_step5 = timeit.default_timer()
        logger.info(f"Pipeline 4. Terminated in {int(start_step5 - start_step4)} seconds")
        state.save_user_scalings()
                
        logger.info(f"Pipeline 5. Score aggregation with {str(self.aggregation)}")
        state = self.aggregation(state)
        start_step6 = timeit.default_timer()
        logger.info(f"Pipeline 5. Terminated in {int(start_step6 - start_step5)} seconds")

        logger.info(f"Pipeline 6. Post-processing scores {str(self.post_process)}")
        state = self.post_process(state)
        end = timeit.default_timer()
        logger.info(f"Pipeline 6. Terminated in {np.round(end - start_step6, 2)} seconds")
        state.save()
        
        logger.info(f"Successful pipeline run, in {int(end - start_step1)} seconds")
        return state
    
    @property
    def trust_propagation(self):
        return self.modules[0]
    
    @trust_propagation.setter
    def trust_propagation(self, value):
        self.modules[0] = value
        
    @property
    def voting_rights_assignment(self):
        return self.modules[1]
    
    @voting_rights_assignment.setter
    def voting_rights_assignment(self, value):
        self.modules[1] = value

    @property
    def preference_learning(self):
        return self.modules[2]
    
    @preference_learning.setter
    def preference_learning(self, value):
        self.modules[2] = value
    
    @property
    def scaling(self):
        return self.modules[3]
    
    @scaling.setter
    def scaling(self, value):
        self.modules[3] = value
        
    @property
    def aggregation(self):
        return self.modules[4]
    
    @aggregation.setter
    def aggregation(self, value):
        self.modules[4] = value
        
    @property
    def post_process(self):
        return self.modules[5]
    
    @post_process.setter
    def post_process(self, value):
        self.modules[5] = value
