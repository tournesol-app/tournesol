from typing import Union
from concurrent.futures import ThreadPoolExecutor, as_completed

import numpy as np
import pandas as pd

from solidago.primitives.dichotomy import solve
from solidago.state import *
from solidago.modules.base import StateFunction


class AffineOvertrust(StateFunction):
    def __init__(self, 
        privacy_penalty: float = 0.5, 
        min_overtrust: float = 2.0,
        overtrust_ratio: float = 0.1,
        *args, **kwargs,
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
        super().__init__(*args, **kwargs)
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
        assessments = assessments.reorder("criterion", "entity_name", "username")
        comparisons = comparisons.reorder("criterion", "entity_name", "username", "other_name")
        stat_names = ("cumulative_trust", "min_voting_right", "overtrust")
        
        entity_names = lambda criterion, judgments: judgments[criterion].keys("entity_name")
        fixed_args = users, made_public, assessments, comparisons
        varying_args = [
            (c, entity_name)
            for c in assessments.keys("criterion") | comparisons.keys("criterion") 
            for entity_name in entity_names(c, assessments) | entity_names(c, comparisons)
        ]
        with ThreadPoolExecutor(max_workers=self.max_workers) as e:
            futures = [e.submit(self.main, *fixed_args, *v_args) for v_args in varying_args]
            for (criterion, entity_name), future in zip(varying_args, as_completed(futures)):
                sub_voting_rights, statistics = future.result()
                for username, voting_right in sub_voting_rights.items():
                    voting_rights[username, entity_name, criterion] = voting_right
                entities.loc[entity_name, [ f"{criterion}_{n}" for n in stat_names ]] = statistics

        return entities, voting_rights
    
    def main(self, 
        users: Users, 
        made_public: MadePublic,
        assessments: Assessments, 
        comparisons: Comparisons, 
        criterion: str, 
        entity_name: str,
    ) -> tuple[dict[str, float], tuple[float, float, float]]:
        """ Computes the allocated voting rights and some statistics of these voting rights
        
        Returns
        -------
        voting_rights: dict[str, float]
            voting_rights[username] is the voting right allocated to username
        statistics: dict[str, float]
            statistics[statistics_name] is the value of statistics_name
        """
        evaluators = assessments[criterion, entity_name].keys("username")
        evaluators |= comparisons[criterion, entity_name].keys("username")
        trust_scores = { u: users.loc[u, "trust_score"] for u in evaluators }
        public = { u: made_public.get(u, entity_name) for u in evaluators }

        voting_rights_np, statistics = self.computing_voting_rights_and_statistics(
            trust_scores=np.nan_to_num(np.array(list(trust_scores.values())), nan=0.0),
            privacy_weights=( np.array(list(public.values())) * (1 - self.privacy_penalty) + self.privacy_penalty )
        )
        voting_rights = {username: voting_rights_np[i] for i, username in enumerate(trust_scores)}
        return voting_rights, statistics

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

