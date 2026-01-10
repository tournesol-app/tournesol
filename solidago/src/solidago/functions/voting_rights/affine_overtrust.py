import itertools
from typing import Union

import numpy as np
import pandas as pd

from solidago.primitives.dichotomy import solve
from solidago.poll import *
from solidago.functions.base import PollFunction
from solidago.primitives.threading import threading


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
            return entities.deepcopy(), VotingRights()

        assessments = assessments.reorder("entity_name", "criterion", "username")
        comparisons = comparisons.reorder("entity_name", "criterion", "username", "other_name")
        made_public = made_public.reorder("entity_name", "username")
        stat_names = ("cumulative_trust", "min_voting_right", "overtrust")
        
        variables = AffineOvertrust._variables(entities, assessments, comparisons)
        evaluators_list = AffineOvertrust._evaluators_list(entities, assessments, comparisons, variables)
        args_lists = self._args_lists(evaluators_list, made_public, variables)
        results = threading(self.max_workers, AffineOvertrust.computing_voting_rights_and_statistics, *args_lists)

        entities, voting_rights = entities.deepcopy(), VotingRights()
        for (entity, criterion), evaluators, (vrights, statistics) in zip(variables, evaluators_list, results):
            for user, voting_right in zip(evaluators, vrights):
                voting_rights[user, entity, criterion] = voting_right
            for name, stat in zip(stat_names, statistics):
                entities[str(entity)][f"{criterion}_{name}"] = stat
        return entities, voting_rights
    
    def _variables(
        entities: Entities, 
        assessments: Assessments, 
        comparisons: Comparisons
    ) -> list[tuple[Entity, str]]:
        def get_criteria(e):
            return assessments[e].keys("criterion") | comparisons[e].keys("criterion")
        return [(e, c) for e in entities for c in get_criteria(e)]
    def _evaluators_list(
        users: Users, 
        assessments: Assessments, 
        comparisons: Comparisons, 
        variables: list[tuple[Entity, str]],
    ) -> list[Users]:
        return [
            users[assessments[e, c].keys("username") | comparisons[e, c].keys("username")]
            for e, c in variables
        ]
    def _args(self,
        evaluators: Users, 
        made_public: MadePublic, # keynames == ["username"]
    ) -> tuple[np.ndarray, np.ndarray, float, float]:
        def get_trust(user):
            return user.trust if hasattr(user, "trust") else 0.0
        trusts = np.array([get_trust(user) for user in evaluators])
        public = np.array([made_public[user] for user in evaluators])
        privacy_weights = public * (1 - self.privacy_penalty) + self.privacy_penalty
        return trusts, privacy_weights, self.overtrust_ratio, self.min_overtrust
    def _args_lists(self,
        evaluators_list: list[Users],
        made_public: MadePublic, # keynames = ["entity", "username"]
        variables: list[tuple[Entity, str]],
    ) -> tuple[list[np.ndarray], list[np.ndarray], list[float], list[float]]:
        return list(zip(*[
            self._args(evaluators, made_public[entity])
            for (entity, _), evaluators in zip(variables, evaluators_list)
        ]))

    def computing_voting_rights_and_statistics(
        trusts: np.ndarray,
        privacy_weights: np.ndarray,
        overtrust_ratio: float,
        min_overtrust: float,
    ) -> tuple[np.ndarray, tuple[float, float, float]]:
        """ Computes voting rights and statistics without having to care about usernames """
        cumulative_trust = (trusts * privacy_weights).sum()
        max_overtrust = cumulative_trust * overtrust_ratio + min_overtrust
        min_voting_right = AffineOvertrust.min_voting_right(max_overtrust, trusts, privacy_weights)
        voting_rights = privacy_weights * trusts.clip(min=min_voting_right)
        return voting_rights, (cumulative_trust, min_voting_right, voting_rights.sum() - cumulative_trust)

    def min_voting_right(max_overtrust: float, trusts: np.ndarray, privacy_weights: np.ndarray) -> float:
        """ Returns the minimal voting rights that corresponds to max_overtrust """
        assert max_overtrust >= 0
        if AffineOvertrust.overtrust(1.0, trusts, privacy_weights) <= max_overtrust:
            return 1.
        return solve(AffineOvertrust.overtrust, max_overtrust, 0, 1, args=(trusts, privacy_weights))

    def overtrust(min_voting_right: float, trusts: np.ndarray, privacy_weights: np.ndarray) -> float:
        return (privacy_weights * (min_voting_right - trusts))[min_voting_right > trusts].sum()

