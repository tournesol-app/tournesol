from typing import Optional, Mapping

import numpy as np
import pandas as pd

from .base import PostProcess
from solidago.scoring_model import ScoringModel, PostProcessedScoringModel


class Squash(PostProcess):
    def __init__(self, score_max: float = 100.0):
        self.score_max = score_max
    
    def __call__(
        self, 
        user_models: Mapping[int, ScoringModel],
        global_model: ScoringModel,
        entities: Optional[pd.DataFrame] = None
    ) -> tuple[Mapping[int, ScoringModel], ScoringModel]:
        """ Post-processes user models and global models,
        typically to yield human-readible scores
        
        Parameters
        ----------
        user_models: user_model[user] should be a ScoringModel to post-process
        global_model: ScoringModel to post-process
        entities: DataFrame with columns
            * entity_id (int, index)
        
        Returns
        -------
        user_models: post-processed user models
        global_model: post-processed global model
        """
        squash = lambda x: self.score_max * x / np.sqrt( 1 + x**2 )
        
        squashed_user_models = {
            u: PostProcessedScoringModel(user_models[u], squash) 
            for u in user_models
        }
        squashed_global_model = PostProcessedScoringModel(global_model, squash)
        return squashed_user_models, squashed_global_model

    def to_json(self):
        return (type(self).__name__, dict(score_max=self.score_max))
