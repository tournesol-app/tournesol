import pandas as pd

from solidago.scoring_model import ScoringModel
from .base import PostProcess


class NoPostProcess(PostProcess):
    def __call__(
        self, 
        user_models: dict[int, ScoringModel],
        global_model: ScoringModel,
        entities: pd.DataFrame
    ) -> tuple[dict[int, ScoringModel], ScoringModel]:
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
        return user_models, global_model
