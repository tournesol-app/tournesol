from abc import ABC, abstractmethod
from typing import Optional, Union

import pandas as pd
import numpy as np

from solidago.judgments import Judgments
from solidago.scoring_model import ScoringModel


class PreferenceLearning(ABC):
    def __call__(
        self, 
        judgments: Judgments,
        users: pd.DataFrame,
        entities: pd.DataFrame,
        initialization: Optional[Union[dict[int, ScoringModel], ScoringModel]] = None
    ) -> ScoringModel:
        """ Learns a scoring model, given user judgments of entities
        
        Parameters
        ----------
        user_judgments: dict[str, pd.DataFrame]
            May contain different forms of judgments, 
            but most likely will contain "comparisons" and/or "assessments"
        entities: DataFrame with columns
            * entity_id: int, index
            * May contain others, such as vector representation
        initialization: dict[int, ScoringModel] or ScoringModel or None
            Starting models, added to facilitate optimization
            It is not supposed to affect the output of the training
            
        Returns
        -------
        model: ScoringModel
        """
        if isinstance(judgments, dict):
            return self.user_learn(judgments, entities, initialization)
        assert isinstance(judgments, Judgments)
        
        user_models = dict() if initialization is None else initialization
        for user, _ in users.iterrows():
            init_model = None
            if initialization is not None and user in initialization:
                init_model = initialization[user]
            user_models[user] = self.user_learn(judgments[user], entities, init_model)
        return user_models
    
    @abstractmethod
    def user_learn(
        self, 
        user_judgments: dict[str, pd.DataFrame],
        entities: pd.DataFrame,
        initialization: Optional[ScoringModel] = None
    ) -> ScoringModel:
        """ Learns a scoring model, given user judgments of entities
        
        Parameters
        ----------
        user_judgments: dict[str, pd.DataFrame]
            May contain different forms of judgments, 
            but most likely will contain "comparisons" and/or "assessments"
        entities: DataFrame with columns
            * entity_id: int, index
            * May contain others, such as vector representation
        initialization: ScoringModel or None
            Starting model, added to facilitate optimization
            It is not supposed to affect the output of the training
            
        Returns
        -------
        model: ScoringModel
        """
        raise NotImplementedError
        
    def to_json(self):
        return (type(self).__name__, )

    def __str__(self):
        return type(self).__name__
