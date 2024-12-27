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

    def __call__(self, state: State) -> None:
        """ Updates state.voting_rights and state.entities by assigning voting rights
        that exceed trust by a limited overtrust amount.
        This overtrust on a given entity on a given criterion is set to be at most 
        an affine function of the total trusts of users who evaluated the entity on the criterion.
        """
        if len(state.users) == 0 or len(state.entities) == 0:
            return None

        state.voting_rights = VotingRights()
        trust_scores = state.users["trust_score"]
        new_records = list()
        for criterion in state.criteria:
            for entity in state.entities:
                voting_rights, statistics = self.compute_per_entity_criterion(state, entity, criterion)
                for username, voting_right in voting_rights.items():
                    state.voting_rights[username, entity, criterion] = voting_right  # type: ignore
                new_records.append((cumulative_trust, min_voting_right, overtrust))

        r = list(zip(*new_records))
        state.entities = state.entities.assign(cumulative_trust=r[0], min_voting_right=r[1], overtrust=r[2])

    def compute_per_entity_criterion(self, 
        state: State, 
        entity: Union[str, "Entity"], 
        criterion: Union[str, "Criterion"]
    ) -> tuple[dict[str, float], dict[str, float]]:
        """ Computes the allocated voting rights and some statistics of these voting rights
        
        Returns
        -------
        voting_rights: dict[str, float]
            voting_rights[username] is the voting right allocated to username
        statistics: dict[str, float]
            statistics[statistics_name] is the value of statistics_name
        """
        usernames = list(state.judgments.get_evaluators(entity, criterion))
        voting_rights, statistics = self.computing_voting_rights_and_statistics(
            trust_scores=np.array([
                state.users.loc[username, "trust_scores"]
                for username in usernames
            ]),
            privacy_weights=np.array([
                1 if state.made_public[username, entities] else self.privacy_penalty
                for username in usernames
            ])
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
        return voting_rights, {
            "cumulative_trust": cumulative_trust,
            "min_voting_right": min_voting_right,
            "overtrust": voting_rights.sum() - cumulative_trust,
        }

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

    def args_save(self) -> dict[str, float]:
        return dict(
            privacy_penalty=self.privacy_penalty, 
            min_overtrust=self.min_overtrust,
            overtrust_ratio=self.overtrust_ratio
        )

    def __str__(self):
        prop_names = ["privacy_penalty", "min_overtrust", "overtrust_ratio"]
        prop = ", ".join([f"{p}={getattr(self, p)}" for p in prop_names])
        return f"{type(self).__name__}({prop})"
