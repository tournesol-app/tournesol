import pandas as pd
import numpy as np

from . import VotingRights, VotingRightsAssignment

from solidago.privacy_settings import PrivacySettings
from solidago.solvers.dichotomy import solve

class AffineOvertrust(VotingRightsAssignment):
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
    
    def __call__(
        self,
        users: pd.DataFrame,
        vouches: pd.DataFrame,
        privacy: PrivacySettings,
    ) -> VotingRights:
        """ Compute voting rights
        
        Parameters
        ----------
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        vouches: DataFrame
            This is not used by VotingRightsWithLimitedOvertrust
        privacy: PrivacySettings
            privacy[user, entity] is the privacy setting of user for entity
            May be True, False or None
        
        Returns
        -------
        voting_rights[user, entity] is the voting right
            of a user on entity for criterion
        """            
        voting_rights = VotingRights()
        if len(users) == 0:
            return voting_rights
        
        for e in privacy.entities():
        
            privacy_weights = { 
                u: self.privacy_penalty if privacy[u, e] else 1 
                for u in privacy.users(e) 
            }
            for u in privacy_weights:
                assert u in users.index, (u, e, privacy.users(e), users)
        
            cumulative_trust = self.cumulative_trust(users, privacy_weights)
            max_overtrust = self.maximal_overtrust(cumulative_trust)
            min_voting_right = self.min_voting_right(max_overtrust, users, privacy_weights)
        
            for u in privacy_weights:
                voting_rights[u, e] = max(min_voting_right, users.loc[u, "trust_score"])
                voting_rights[u, e] *= privacy_weights[u]
        
        return voting_rights
    
    def cumulative_trust(
        self,
        users: pd.DataFrame,
        privacy_weights: dict[int, float]
    ) -> float:
        """ Returns the sum of trusts of raters of entity entity_id, 
        weighted by their privacy setting.
        
        Parameters
        ----------
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        privacy_weights: dict[int, float]
            privacy_weights[u] is the privacy weight of user u
            
        Returns
        -------
        out: float
        """
        trust = 0
        for user in privacy_weights:
            trust += privacy_weights[user] * users.loc[user, "trust_score"]
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
        privacy_weights: dict[int, float]
    ) -> float:
        """ Returns the overtrust, if min_voting_right is enforced upon all raters.
        
        Parameters
        ----------
        min_voting_right: float
            Overtrust for min_voting_right
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        privacy_weights: dict[int, float]
            privacy_weights[u] is the privacy weight of user u
            
        Returns
        -------
        out: float
        """
        overtrust = 0
        for user in privacy_weights:
            user_trust = users.loc[user, "trust_score"]
            overtrust += privacy_weights[user] * max(min_voting_right - user_trust, 0)
        return overtrust
    
    def min_voting_right(
        self,
        max_overtrust: float,
        users: pd.DataFrame,
        privacy_weights: dict[int, float]
    ) -> float:
        """ Returns the minimal voting rights that corresponds to max_overtrust.
        
        Parameters
        ----------
        max_overtrust: float
            Maximal overtrust allowed for entity_id
        users: DataFrame with columns
            * user_id (int, index)
            * trust_score (float)
        privacy_weights: dict[int, float]
            privacy_weights[u] is the privacy weight of user u
            
        Returns
        -------
        out: float
        """
        assert max_overtrust >= 0
        def overtrust(min_voting_right):
            return self.overtrust(min_voting_right, users, privacy_weights)
        
        if overtrust(1) <= max_overtrust:
            return 1.0
        
        return solve(overtrust, max_overtrust, 0, 1)
