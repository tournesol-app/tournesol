from typing import Mapping

import pandas as pd
import numpy as np

from .base import Scaling

from solidago.privacy_settings import PrivacySettings
from solidago.scoring_model import ScoringModel, ScaledScoringModel
from solidago.voting_rights import VotingRights
from solidago.primitives import qr_quantile


class QuantileShift(Scaling):
    def __init__(
        self,
        quantile: float = 0.15,
        *,
        target_score: float = 0.0,
        lipschitz: float = 0.1,
        error: float = 1e-5,
    ):
        """The scores are shifted so that their quantile zero_quantile equals zero

        Parameters
        ----------
        zero_quantile: float
        """
        self.quantile = quantile
        self.target_score = target_score
        self.lipschitz = lipschitz
        self.error = error

    def __call__(
        self,
        user_models: Mapping[int, ScoringModel],
        users: pd.DataFrame,
        entities: pd.DataFrame,
        voting_rights: VotingRights,
        privacy: PrivacySettings,
    ) -> dict[int, ScaledScoringModel]:
        """Returns scaled user models

        Parameters
        ----------
        user_models: dict[int, ScoringModel]
            user_models[user] is user's scoring model
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        entities: DataFrame with columns
            * entity_id (int, ind)
        voting_rights: VotingRights
            voting_rights[user, entity]: float
        privacy: PrivacySettings
            privacy[user, entity] in { True, False, None }

        Returns
        -------
        out[user]: ScoringModel
            Will be scaled by the Scaling method
        """
        weights = []
        scores, lefts, rights = [], [], []
        for user_id, user_model in user_models.items():
            n_entities = 0
            for entity_id, output in user_model.iter_entities(entities):
                n_entities += 1
                scores.append(output[0])
                lefts.append(output[1])
                rights.append(output[2])
            if n_entities > 0:
                weights.extend([1 / n_entities] * n_entities)

        shift = -qr_quantile(
            lipschitz=self.lipschitz,
            quantile=self.quantile,
            values=np.array(scores),
            voting_rights=np.array(weights),
            left_uncertainties=np.array(lefts),
            right_uncertainties=np.array(rights),
            error=self.error,
        ) + self.target_score

        return {
            user: ScaledScoringModel(user_model, translation=shift)
            for (user, user_model) in user_models.items()
        }

    def to_json(self):
        return type(self).__name__, dict(
            quantile=self.quantile,
            target_score=self.target_score,
            lipschitz=self.lipschitz,
            error=self.error
        )

    def __str__(self):
        prop_names = ["quantile", "lipschitz", "error", "target_score"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"


class QuantileZeroShift(QuantileShift):
    def __init__(
        self,
        zero_quantile: float = 0.15,
        *,
        lipschitz: float = 0.1,
        error: float = 0.00001
    ):
        super().__init__(zero_quantile, target_score=0.0, lipschitz=lipschitz, error=error)

    def to_json(self):
        return type(self).__name__, dict(
            zero_quantile=self.quantile,
            lipschitz=self.lipschitz,
            error=self.error
        )
