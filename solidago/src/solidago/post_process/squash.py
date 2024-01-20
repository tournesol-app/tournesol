from abc import ABC, abstractmethod

import numpy as np

from . import PostProcess
from solidago.scoring_model import ScoringModel, PostProcessedScoringModel


class Squash(PostProcess):
    def __init__(self, score_max: float = 100):
        self.score_max = score_max
    
    def __call__(
        self, 
        user_models: dict[int, ScoringModel],
        global_model: ScoringModel
    ) -> tuple[dict[int, ScoringModel], ScoringModel]:
        """ Post-processes user models and global models,
        typically to yield human-readible scores
        
        Parameters
        ----------
        user_models: user_model[user] should be a ScoringModel to post-process
        global_model: ScoringModel to post-process
        
        Returns
        -------
        user_models: post-processed user models
        global_model: post-processed global model
        """
        squash = lambda x: self.score_max * x / np.sqrt( 1 + x**2 )
        
        squasheded_user_models = {
            u: PostProcessedScoringModel(user_models[u], squash) 
            for u in user_models
        }
        squashed_global_model = PostProcessedScoringModel(global_model, squash)
        
        return squash_user_models, squashed_global_model
