from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import logging

from solidago.judgments import Judgments
from solidago.scoring_model import ScoringModel


logger = logging.getLogger(__name__)


class PreferenceLearning(ABC):
    def __call__(self, state: State) -> None:
        state.user_models = self.learn(
            state.users, 
            state.entities, 
            state.criteria, 
            state.judgments,
            state.user_models
        )
    
    def learn(self,
        users: Users,
        entities: Entities,
        criteria: Criteria,
        judgments: Judgments,
        user_models: UserModels
    ) -> UserModels:
        """ Learns a scoring model, given user judgments of entities """
        assert isinstance(judgments, Judgments)
        for user in users:
            init_model = user_models[user]
            user_models[user] = self.user_learn(state.judgments, entities, init_model, new_judg)
        return user_models

    @abstractmethod
    def user_learn(
        self,
        user_judgments: dict[str, pd.DataFrame],
        entities: pd.DataFrame,
        initialization: Optional[ScoringModel] = None,
        new_judgments: Optional[dict[str, pd.DataFrame]] = None,
    ) -> ScoringModel:
        """Learns a scoring model, given user judgments of entities

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
        new_judgments:
            New judgments
            This allows to prioritize coordinate descent, starting with newly evaluated entities

        Returns
        -------
        model: ScoringModel
        """
        raise NotImplementedError

    def to_json(self) -> tuple:
        return (type(self).__name__,)

    def __str__(self):
        return type(self).__name__
