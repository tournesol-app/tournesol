from typing import Union

import numpy as np
import pandas as pd

from solidago.primitives.dichotomy import solve
from solidago.state import *
from .base import VotingRightsAssignment


class AffineOvertrust(VotingRightsAssignment):
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

    def main(self, 
        users: Users, 
        entities: Entities, 
        made_public: MadePublic,
        assessments: Assessments, 
        comparisons: Comparisons
    ) -> tuple[Entities, VotingRights]:
        """ Updates state.voting_rights and state.entities by assigning voting rights
        that exceed trust by a limited overtrust amount.
        This overtrust on a given entity on a given criterion is set to be at most 
        an affine function of the total trusts of users who evaluated the entity on the criterion.
        """
        if len(users) == 0 or len(entities) == 0:
            return None

        voting_rights = VotingRights()
        trust_scores = state.users["trust_score"]
        new_records = list()
        criteria = assessments.get_set("criterion") | comparisons.get_set("criterion")
        statistics_list = list()
        for entity in entities:
            assessment_evaluators = assessments.get_evaluators_by_criterion(entity)
            comparison_evaluators = comparisons.get_evaluators_by_criterion(entity)
            entity_statistics = list()
            for criterion in criteria:
                evaluators = assessment_evaluators[criterion] | comparison_evaluators[criterion]
                trust_scores = { username: users.loc[username, "trust_score"] for username in evaluators }
                public = { username: made_public[username, entity] for username in evaluators }
                sub_voting_rights, sub_statistics = self.sub_main(trust_scores, public)
                for username in sub_voting_rights:
                    voting_rights.add_row((username, entity), { criterion: voting_right })
                entity_statistics += [ cumulative_trust, min_voting_right, overtrust ]
            statistics_list.append(entity_statistics)

        statistics = list(zip(*statistics_list))
        entities_with_stats = entities
        for index, criterion in enumerate(criteria):
            entities_with_stats[f"{criterion}_cumulative_trust"] = statistics[3*index]
            entities_with_stats[f"{criterion}_min_voting_right"] = statistics[3*index + 1]
            entities_with_stats[f"{criterion}_overtrust"] = statistics[3*index + 2]
        return entities_with_stats, voting_rights

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
            trust_scores=np.array(list(trust_scores.values())),
            privacy_weights=( np.array(list(public.values())) * (1 - self.privacy) + self.privacy )
        )
        return { username: voting_rights[i] for i, username in enumerate(usernames) }, statistics
        

    def computing_voting_rights_and_statistics(self,
        trust_scores: np.ndarray,
        privacy_weights: np.ndarray,
    ) -> tuple[np.ndarray, dict[str, float]]:
        """ Computes voting rights and statistics without having to care about usernames """
        trust_scores = trust_scores.nan_to_num(nan=0.)
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

