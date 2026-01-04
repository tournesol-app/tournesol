from typing import Union

import numpy as np
import pandas as pd

from solidago.primitives.dichotomy import solve
from solidago.poll import *
from solidago.functions.base import PollFunction


class AffineOvertrust(PollFunction):
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
            return entities, VotingRights()

        voting_rights = VotingRights()
        assessments = assessments.reorder("entity_name", "criterion", "username")
        comparisons = comparisons.reorder("entity_name", "criterion", "username", "other_name")
        made_public = made_public.reorder("entity_name", "username")
        stat_names = ("cumulative_trust", "min_voting_right", "overtrust")
        entities = entities.deepcopy()
        eval_entities = entities[assessments.keys("entity_name") | comparisons.keys("entity_name")]
        args = users, eval_entities, made_public, assessments, comparisons

        if self.max_workers == 1:
            for (entity_name, criterion), (vrights, statistics) in self.batch(0, *args).items():
                for username, voting_right in vrights.items():
                    voting_rights[username, entity_name, criterion] = voting_right
                for name, stat in zip(stat_names, statistics):
                    entities[entity_name][f"{criterion}_{name}"] = stat
            return entities, voting_rights

        from concurrent.futures import ProcessPoolExecutor, as_completed
        with ProcessPoolExecutor(max_workers=self.max_workers) as e:
            futures = {e.submit(self.batch, i, *args) for i in range(self.max_workers)}
            for f in as_completed(futures):
                for (entity_name, criterion), (vrights, statistics) in f.result().items():
                    for username, voting_right in vrights.items():
                        voting_rights[username, entity_name, criterion] = voting_right
                    for name, stat in zip(stat_names, statistics):
                        entities[entity_name][f"{criterion}_{name}"] = stat
        return entities, voting_rights
    
    def batch(self, 
        batch_number: int,
        users: Users,
        entities: Entities, 
        made_public: MadePublic, # keynames == ["entity_name", "username"]
        assessments: Assessments, # keynames == ["entity_name", "criterion", "username"]
        comparisons: Comparisons, # keynames == ["entity_name", "criterion", "username", "other_name"]
    ) -> dict[tuple[str, str], dict[str, float], tuple[float, float, float]]:
        indices = range(batch_number, len(entities), self.max_workers)
        batch_entities = {entities.get_by_index(i) for i in indices}
        return {
            (e.name, c): self.main(users, made_public[e], assessments[e, c], comparisons[e, c]) 
            for e in batch_entities
            for c in assessments[e].keys("criterion") | comparisons[e].keys("criterion")
        }
    
    def main(self, 
        users: Users, 
        made_public: MadePublic, # keynames == ["username"]
        assessments: Assessments, # keynames == ["username"] 
        comparisons: Comparisons, # keynames == ["username"]
    ) -> tuple[dict[str, float], tuple[float, float, float]]:
        """ Computes the allocated voting rights and some statistics of these voting rights
        
        Returns
        -------
        voting_rights: dict[str, float]
            voting_rights[username] is the voting right allocated to username
        statistics: dict[str, float]
            statistics[statistics_name] is the value of statistics_name
        """
        evaluators = users[assessments.keys("username") | comparisons.keys("username")]
        trusts = {user.name: user.trust for user in evaluators}
        public = {user.name: made_public[user] for user in evaluators}

        voting_rights_np, statistics = self.computing_voting_rights_and_statistics(
            trusts=np.nan_to_num(np.array(list(trusts.values())), nan=0.0),
            privacy_weights=( np.array(list(public.values())) * (1 - self.privacy_penalty) + self.privacy_penalty )
        )
        voting_rights = {username: voting_rights_np[i] for i, username in enumerate(trusts)}
        return voting_rights, statistics

    def computing_voting_rights_and_statistics(self,
        trusts: np.ndarray,
        privacy_weights: np.ndarray,
    ) -> tuple[np.ndarray, tuple[float, float, float]]:
        """ Computes voting rights and statistics without having to care about usernames """
        cumulative_trust = (trusts * privacy_weights).sum()
        max_overtrust = self.maximal_overtrust(cumulative_trust)
        min_voting_right = self.min_voting_right(max_overtrust, trusts, privacy_weights)
        voting_rights = privacy_weights * trusts.clip(min=min_voting_right)
        return voting_rights, (cumulative_trust, min_voting_right, voting_rights.sum() - cumulative_trust)

    def maximal_overtrust(self, cumulative_trust: float) -> float:
        """Computes the maximal allowed overtrust of an entity,
        for a given total trust of the entity's raters """
        return cumulative_trust * self.overtrust_ratio + self.min_overtrust 

    def min_voting_right(self,
        max_overtrust: float,
        trusts: np.ndarray,
        privacy_weights: np.ndarray,
    ) -> float:
        """ Returns the minimal voting rights that corresponds to max_overtrust """
        assert max_overtrust >= 0

        def overtrust(min_voting_right):
            return self.overtrust(min_voting_right, trusts, privacy_weights)

        if overtrust(1) <= max_overtrust:
            return 1.

        return solve(overtrust, max_overtrust, 0, 1)

    def overtrust(self,
        min_voting_right: float,
        trusts: np.ndarray,
        privacy_weights: np.ndarray,
    ) -> float:
        """ Returns the overtrust, if min_voting_right is enforced upon all raters.

        Parameters
        ----------
        min_voting_right: float
            Overtrust for min_voting_right
        trusts: Series with index user_id (int)
            values: trusts (float)
        privacy_weights: Series with index user_id (int)
            values: privacy weight of user

        Returns
        -------
        out: float
        """
        return (privacy_weights * (min_voting_right - trusts))[
            min_voting_right > trusts
        ].sum()

