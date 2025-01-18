from typing import Union

import numpy as np
import pandas as pd

from solidago.primitives.dichotomy import solve
from solidago._state import *
from solidago._pipeline.base import StateFunction


class AffineOvertrust(StateFunction):
    def __init__(self, 
        privacy_penalty: float = 0.5, 
        min_overtrust: float = 2.0,
        overtrust_ratio: float = 0.1,
    ):
        """ Computes voting_rights using the affine overtrust algorithm described in 
        "Solidago: A Modular Pipeline for Collaborative Scoring" by Lê Nguyên Hoang, 
        Romain Beylerian, Bérangère Colbois, Julien Fageot, Louis Faucon, Aidan Jungo, 
        Alain Le Noac'h, Adrien Matissart, Oscar Villemaud, last updated in September 2024.
        
        Parameters
        ----------
        privacy_penalty: float
            Penalty on private entity evaluation
        """
        self.privacy_penalty = privacy_penalty
        self.min_overtrust = min_overtrust
        self.overtrust_ratio = overtrust_ratio

    def __call__(self, 
        users: Users, 
        entities: Entities, 
        made_public: MadePublic,
        assessments: Assessments, 
        comparisons: Comparisons
    ) -> tuple[Entities, VotingRights]:
        """ Updates voting_rights and entities by assigning voting rights
        that exceed trust by a limited overtrust amount.
        This overtrust on a given entity on a given criterion is set to be at most 
        an affine function of the total trusts of users who evaluated the entity on the criterion.
        """
        if len(users) == 0 or len(entities) == 0:
            return None

        voting_rights = VotingRights()
        assessments = assessments.reorder_keys(["criterion", "entity_name", "username"])
        comparisons = comparisons.reorder_keys(["criterion", "left_name", "right_name", "username"])
        
        for criterion in assessments.get_set("criterion") | comparisons.get_set("criterion"):
            entity_names = assessments[criterion].get_set("entity_name")
            ordered_comparisons = comparisons[criterion].order_by_entities(other_keys_first=True)
            ordered_comparisons = ordered_comparisons.reorder_keys(["entity_name", "username", "other_name"])
            entity_names |= ordered_comparisons.get_set("entity_name")

            for entity_name in entity_names:
                evaluators = assessments[criterion, entity_name].get_set("username")
                evaluators |= ordered_comparisons[entity_name].get_set("username")
                trust_scores = { username: users.loc[username, "trust_score"] for username in evaluators }
                public = { username: made_public[username, entity_name] for username in evaluators }
                sub_voting_rights, sub_statistics = self.sub_main(trust_scores, public)

                for username, voting_right in sub_voting_rights.items():
                    voting_rights[username, entity_name, criterion] = voting_right

                cumulative_trust, min_voting_right, overtrust = sub_statistics
                entities.loc[entity_name, f"{criterion}_cumulative_trust"] = cumulative_trust
                entities.loc[entity_name, f"{criterion}_min_voting_right"] = min_voting_right
                entities.loc[entity_name, f"{criterion}_overtrust"] = overtrust
                
        return entities, voting_rights

    def sub_main(self, 
        trust_scores: dict[str, float],
        public: dict[str, bool],
    ) -> tuple[dict[str, float], tuple[float, float, float]]:
        """ Computes the allocated voting rights and some statistics of these voting rights
        
        Returns
        -------
        voting_rights: dict[str, float]
            voting_rights[username] is the voting right allocated to username
        statistics: dict[str, float]
            statistics[statistics_name] is the value of statistics_name
        """
        voting_rights, statistics = self.computing_voting_rights_and_statistics(
            trust_scores=np.nan_to_num(np.array(list(trust_scores.values())), nan=0.0),
            privacy_weights=( np.array(list(public.values())) * (1 - self.privacy_penalty) + self.privacy_penalty )
        )
        return { username: voting_rights[i] for i, username in enumerate(trust_scores) }, statistics

    def computing_voting_rights_and_statistics(self,
        trust_scores: np.ndarray,
        privacy_weights: np.ndarray,
    ) -> tuple[np.ndarray, tuple[float, float, float]]:
        """ Computes voting rights and statistics without having to care about usernames """
        cumulative_trust = (trust_scores * privacy_weights).sum()
        max_overtrust = self.maximal_overtrust(cumulative_trust)
        min_voting_right = self.min_voting_right(max_overtrust, trust_scores, privacy_weights)
        voting_rights = privacy_weights * trust_scores.clip(min=min_voting_right)
        return voting_rights, (cumulative_trust, min_voting_right, voting_rights.sum() - cumulative_trust)

    def maximal_overtrust(self, cumulative_trust: float) -> float:
        """Computes the maximal allowed overtrust of an entity,
        for a given total trust of the entity's raters """
        return cumulative_trust * self.overtrust_ratio + self.min_overtrust 

    def min_voting_right(self,
        max_overtrust: float,
        trust_scores: np.ndarray,
        privacy_weights: np.ndarray,
    ) -> float:
        """ Returns the minimal voting rights that corresponds to max_overtrust """
        assert max_overtrust >= 0

        def overtrust(min_voting_right):
            return self.overtrust(min_voting_right, trust_scores, privacy_weights)

        if overtrust(1) <= max_overtrust:
            return 1.

        return solve(overtrust, max_overtrust, 0, 1)

    def overtrust(self,
        min_voting_right: float,
        trust_scores: np.ndarray,
        privacy_weights: np.ndarray,
    ) -> float:
        """ Returns the overtrust, if min_voting_right is enforced upon all raters.

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

