from abc import ABC, abstractmethod
from typing import Optional

import pandas as pd
import logging

from solidago.judgments import Judgments
from solidago.scoring_model import ScoringModel


logger = logging.getLogger(__name__)


class PreferenceLearning(ABC):
    MAX_UNCERTAINTY = 1000.0

    def __call__(
        self,
        judgments: Judgments,
        users: pd.DataFrame,
        entities: pd.DataFrame,
        initialization: Optional[dict[int, ScoringModel]] = None,
        new_judgments: Optional[Judgments] = None,
    ) -> dict[int, ScoringModel]:
        """Learns a scoring model, given user judgments of entities

        Parameters
        ----------
        judgments:
            May contain different forms of judgments,
            but most likely will contain "comparisons" and/or "assessments"
        entities: DataFrame with columns
            * entity_id: int, index
            * May contain others, such as vector representation
        initialization: dict[int, ScoringModel] or ScoringModel or None
            Starting models, added to facilitate optimization
            It is not supposed to affect the output of the training
        new_judgments:
            New judgments
            This allows to prioritize coordinate descent, starting with newly evaluated entities

        Returns
        -------
        user_models: dict[int, ScoringModel]
            user_models[user] is the learned scoring model for user
        """
        assert isinstance(judgments, Judgments)

        user_models = dict() if initialization is None else initialization
        for n_user, user in enumerate(users.index):
            if n_user % 100 == 0:
                logger.info(f"  Preference learning for user {n_user} out of {len(users)}")
            else:
                logger.debug(f"  Preference learning for user {n_user} out of {len(users)}")
            init_model = None
            if initialization is not None:
                init_model = initialization.get(user)
            new_judg = None if new_judgments is None else new_judgments[user]
            user_judgments = judgments[user]
            if user_judgments is None:
                continue
            user_models[user] = self.user_learn(user_judgments, entities, init_model, new_judg)
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
