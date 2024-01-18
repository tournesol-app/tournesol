import pandas as pd
import numpy as np

from . import VotingRights
from solidago.solvers.dichotomy import solve

class VotingRightsWithLimitedOvertrust(VotingRights):
    def __init__(
        self, 
        privacy_penalty: float = 0.5, 
        min_overtrust: float = 2.0,
        overtrust_ratio: float = 0.1,
    ):
        """ privately scored entities are given 
        
        Parameters
        ----------
        privacy_penalty: float
            Penalty on private comparisons
        """
        self.privacy_penalty = privacy_penalty
        self.min_overtrust = min_overtrust
        self.overtrust_ratio = overtrust_ratio
    
    def cumulative_trust(
        self,
        users: pd.DataFrame,
        privacy_weight: dict[int, float]
    ) -> float:
        """ Returns the sum of trusts of raters of entity entity_id, 
        weighted by their privacy setting.
        
        Parameters
        ----------
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        privacy_weight: dict[int, float]
            privacy_weight[u] is the privacy weight of user u
            
        Returns
        -------
        out: float
        """
        trust = 0
        for user in privacy_weight:
            trust += privacy_weight[user] * users.loc[user, "trust_score"]
        return trust
    
    def maximal_overtrust(self, trust: float) -> float:
        """ Computes the maximal allowed overtrust of an entity,
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
        users: pd.DataFrame,
        privacy_weight: dict[int, float]
    ) -> float:
        """ Returns the overtrust, if min_voting_right is enforced upon all raters.
        
        Parameters
        ----------
        min_voting_right: float
            Overtrust for min_voting_right
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        privacy_weight: dict[int, float]
            privacy_weight[u] is the privacy weight of user u
            
        Returns
        -------
        out: float
        """
        overtrust = 0
        for user in privacy_weight:
            user_trust = users.loc[user, "trust_score"]
            overtrust += privacy_weight[user] * max(min_voting_right - user_trust, 0)
        return overtrust
    
    def min_voting_right(
        self,
        max_overtrust: float,
        users: pd.DataFrame,
        privacy_weight: dict[int, float]
    ) -> float:
        """ Returns the minimal voting rights that corresponds to max_overtrust.
        
        Parameters
        ----------
        max_overtrust: float
            Maximal overtrust allowed for entity_id
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        privacy_weight: dict[int, float]
            privacy_weight[u] is the privacy weight of user u
            
        Returns
        -------
        out: float
        """
        assert max_overtrust >= 0
        def overtrust(min_voting_right):
            return self.overtrust(min_voting_right, entity_id, users, privacy)
        
        if overtrust(1) <= max_overtrust:
            return 1.0
        
        return solve(overtrust, max_overtrust, 0, 1)
    
    def __call__(
        self,
        users: pd.DataFrame,
        vouches: pd.DataFrame,
        privacy: pd.DataFrame,
        comparisons: pd.DataFrame
    ) -> dict[int, dict[int, float]]:
        """ Compute voting rights
        
        Parameters
        ----------
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        vouches: DataFrame
            This is not used by VotingRightsWithLimitedOvertrust
        privacy: DataFrame with columns
            * `user_id`
            * `entity_id`
            * `is_public`
        comparisons: DataFrame with columns
            * user_id (int)
            * entity_a (int)
            * entity_b (int)
            * score (float)
        
        Returns
        -------
        voting_rights[user][entity][criterion] is the voting right
            of a user on entity for criterion
        """
        voting_rights = dict()
        n_entities = privacy["entity_id"].max()
        n_entities = max(n_entities, comparisons["entity_id"])
        
        for e in range(n_entities):
        
            privacy_weight = dict()
            c = comparisons[comparisons["entity_a"] == e or comparisons["entity_b"] == e]
            for _, row in privacy[privacy["entity_id"] == e].iterrows():
                u = row["user_id"]
                if len(c[c["user_id"] == u]) == 0:
                    continue
                privacy_weight[u] = 1 if row["is_public"] else self.privacy_penalty
        
            cumulative_trust = self.cumulative_trust(users, privacy_weight)
            max_overtrust = self.maximal_overtrust(cumulative_trust)
            min_voting_right = self.min_voting_right(max_overtrust, users, privacy_weight)
        
            voting_rights[e] = dict()
            for u in privacy_weight:
                voting_rights[u] = max(min_voting_right, users.loc[u, "trust_score"])
                voting_rights[u] *= privacy_weight[user]
        
        return voting_rights
