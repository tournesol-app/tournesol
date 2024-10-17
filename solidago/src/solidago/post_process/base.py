from abc import ABC, abstractmethod
from typing import Mapping

import pandas as pd

from solidago.scoring_model import ScoringModel


class PostProcess(ABC):
    @abstractmethod
    def __call__(
        self, 
        user_models: Mapping[int, ScoringModel],
        global_model: ScoringModel,
        entities: pd.DataFrame
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
        raise NotImplementedError
        
    def to_json(self) -> tuple:
        return (type(self).__name__, )
