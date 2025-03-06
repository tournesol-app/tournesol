from collections import defaultdict
from typing import Optional

import numpy as np
import pandas as pd

from solidago import PrivacySettings, ScoringModel
from solidago.solvers.dichotomy import solve
from .base import VotingRights, VotingRightsAssignment


class AffineOvertrust(VotingRightsAssignment):
    def __init__(
        self,
        privacy_penalty: float = 0.5,
        min_overtrust: float = 2.0,
        overtrust_ratio: float = 0.1,
    ):
        """
        Parameters
        ----------
        privacy_penalty: float
            Penalty on private comparisons
        min_overtrust: float
        overtrust_ratio: float
        """
        self.privacy_penalty = privacy_penalty
        self.min_overtrust = min_overtrust
        self.overtrust_ratio = overtrust_ratio

    def __call__(
        self,
        users: pd.DataFrame,
        entities: pd.DataFrame,
        vouches: pd.DataFrame,
        privacy: PrivacySettings,
        user_models: Optional[dict[int, ScoringModel]],
    ) -> tuple[VotingRights, pd.DataFrame]:
        """Compute voting rights.

        Parameters
        ----------
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        entities: DataFrame with columns
            * entity_id (int, index)
        vouches: not used
        privacy: PrivacySettings
            privacy[user, entity] is the privacy setting of user for entity
            May be True, False or None
        user_models: scoring model per user

        Returns
        -------
        voting_rights[user, entity] is the voting right
            of a user on entity for criterion
        entities: DataFrame with columns
            * entity_id (int, index)
            * cumulative_trust (float)
            * min_voting_right (float)
            * overtrust (float)
        """
        voting_rights = VotingRights()
        if len(users) == 0 or len(entities) == 0:
            return voting_rights, entities

        entity_to_users: dict[int, set[int]] = {
            entity_id: set()
            for entity_id in entities.index
        }
        if user_models is None:
            # In this case it's assumed that for any pair (entity, user) the privacy
            # is defined if and only if `user` expressed a judgement on `entity`.
            for entity_id in privacy.entities():
                entity_to_users[entity_id] = privacy.users(entity_id)
        else:
            for user_id, model in user_models.items():
                for entity_id in model.scored_entities():
                    entity_to_users[entity_id].add(user_id)

        trust_scores = users["trust_score"]
        new_records = []
        for entity_id, user_ids in entity_to_users.items():
            privacy_weights = pd.Series(
                {u: self.privacy_penalty if privacy[u, entity_id] else 1.0 for u in user_ids}
            )
            (voting_rights_series, cumulative_trust, min_voting_right, overtrust) = (
                self.compute_entity_voting_rights(
                    trust_scores=trust_scores,
                    privacy_weights=privacy_weights,
                )
            )
            for user_id, voting_right in voting_rights_series.items():
                voting_rights[user_id, entity_id] = voting_right  # type: ignore
            new_records.append((cumulative_trust, min_voting_right, overtrust))

        r = list(zip(*new_records))
        entities = entities.assign(cumulative_trust=r[0], min_voting_right=r[1], overtrust=r[2])
        return voting_rights, entities

    def compute_entity_voting_rights(
        self,
        trust_scores: pd.Series,
        privacy_weights: pd.Series,
    ) -> tuple[pd.Series, float, float, float]:
        trust_scores_np = trust_scores[privacy_weights.index].fillna(0.0).to_numpy()
        privacy_weights_np = privacy_weights.to_numpy()
        cumulative_trust = self.cumulative_trust(trust_scores_np, privacy_weights_np)
        max_overtrust = self.maximal_overtrust(cumulative_trust)
        min_voting_right = self.min_voting_right(
            max_overtrust, trust_scores_np, privacy_weights_np
        )
        voting_rights = pd.Series(
            privacy_weights_np * trust_scores_np.clip(min=min_voting_right),
            index=privacy_weights.index,
        )
        return (
            voting_rights,
            cumulative_trust,
            min_voting_right,
            voting_rights.sum() - cumulative_trust,
        )

    def cumulative_trust(
        self,
        trust_scores: np.ndarray,
        privacy_weights: np.ndarray,
    ) -> float:
        """Returns the sum of trusts of raters of entity entity_id,
        weighted by their privacy setting.

        Parameters
        ----------
        trust_scores: Series with
            * index "user_id (int, index)
            * values "trust_score" (float)
        privacy_weights: dict[int, float]
            privacy_weights[u] is the privacy weight of user u

        Returns
        -------
        out: float
        """
        return (trust_scores * privacy_weights).sum()

    def maximal_overtrust(self, trust: float) -> float:
        """Computes the maximal allowed overtrust of an entity,
        for a given total trust of the entity's raters.

        Parameters
        ----------
        trust: float
            Cumulative trust received by the entity

        Returns
        -------
        out: float
        """
        return trust * self.overtrust_ratio + self.min_overtrust

    def overtrust(
        self,
        min_voting_right: float,
        trust_scores: np.ndarray,
        privacy_weights: np.ndarray,
    ) -> float:
        """Returns the overtrust, if min_voting_right is enforced upon all raters.

        Parameters
        ----------
        min_voting_right: float
            Overtrust for min_voting_right
        trust_scores: Series with index user_id (int)
            values: trust_score (float)
        privacy_weights: Series with index user_id (int)
            values: privacy weight of user

        Returns
        -------
        out: float
        """
        return (privacy_weights * (min_voting_right - trust_scores))[
            min_voting_right > trust_scores
        ].sum()

    def min_voting_right(
        self,
        max_overtrust: float,
        trust_scores: np.ndarray,
        privacy_weights: np.ndarray,
    ) -> float:
        """Returns the minimal voting rights that corresponds to max_overtrust.

        Parameters
        ----------
        max_overtrust: float
            Maximal overtrust allowed for entity_id
        trust_scores:
            trust score values per user
        privacy_weights: dict[int, float]
            privacy weight per user

        Returns
        -------
        out: float
        """
        assert max_overtrust >= 0

        def overtrust(min_voting_right):
            return self.overtrust(min_voting_right, trust_scores, privacy_weights)

        if overtrust(1) <= max_overtrust:
            return 1.0

        return solve(overtrust, max_overtrust, 0, 1)

    def to_json(self):
        return "AffineOvertrust", dict(
            privacy_penalty=self.privacy_penalty,
            min_overtrust=self.min_overtrust,
            overtrust_ratio=self.overtrust_ratio,
        )

    def __str__(self):
        prop_names = ["privacy_penalty", "min_overtrust", "overtrust_ratio"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"
