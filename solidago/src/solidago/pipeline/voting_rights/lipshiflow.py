import numpy as np
import pandas as pd

from solidago import PrivacySettings
from .base import VotingRights, VotingRightsAssignment


class LipschiFlow(VotingRightsAssignment):
    def __init__(
        self, 
        max_voting_right: float,
        lipschitz: float,
        epsilon: float
    ):
        """ privately scored entities are given 
        
        Parameters
        ----------
        privacy_penalty: float
            Penalty on private comparisons
        """
        self.max_voting_right = max_voting_right
        self.lipschitz = lipschitz
        self.epsilon

    def __call__(
        self,
        users: pd.DataFrame,
        entities: pd.DataFrame,
        vouches: pd.DataFrame,
        privacy: PrivacySettings,
        user_models: dict[int, "ScoringModel"]
    ) -> tuple[VotingRights, pd.DataFrame]:
        """Compute voting rights

        Parameters
        ----------
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        entities: DataFrame with columns
            * entity_id (int, index)
        vouches: DataFrame
            This is not used by VotingRightsWithLimitedOvertrust
        privacy: PrivacySettings
            privacy[user, entity] is the privacy setting of user for entity
            May be True, False or None

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
        
        for entity_id, entity in entities.iterrows():
            state = NetworkState(users, entity, vouches, privacy, users)
            while state.relay.sum() > self.epsilon:
                state = self.forward(users, state)
                state = self.backward(users, state)
            voting_rights = state.assign(entity, voting_rights)
        return voting_rights, entities

    def forward(self, users, state):
        raise NotImplemented

    def backward(self, users, state):
        raise NotImplemented
        
    def assign(self, entity, voting_rights):
        raise NotImplemented
        
    def to_json(self):
        return self.__class__.__name__, dict(
            max_voting_right=self.max_voting_right, 
            lipschitz=self.lipschitz
        )

    def __str__(self):
        prop_names = ["max_voting_right", "lipschitz"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"


class NetworkState:
    def __init__(self, users, entities, vouches, privacy):
        self.index_to_user_id = users.user_id
        self.entity = entities
        self.vouches = vouches
        self.privacy = privacy
        self.relay = users.trust_score
        self.cumulative_relay = np.zeros(len(users))
        self.assigned = np.zeros(len(users))
        self.cumulative_flow = [dict() for _ in users]

    def assign(self, entity, voting_rights):
        raise NotImplemented
