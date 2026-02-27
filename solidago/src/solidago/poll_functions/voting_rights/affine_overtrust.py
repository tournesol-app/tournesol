from copy import deepcopy
from numpy.typing import NDArray

import numpy as np

from solidago.primitives.dichotomy import solve
from solidago.poll import *
from solidago.poll_functions.parallelized import ParallelizedPollFunction


class AffineOvertrust(ParallelizedPollFunction):
    block_parallelization: bool = False
    
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

    def _variables(self, # type: ignore
        entities: Entities, 
        ratings: Ratings,
        comparisons: Comparisons,
    ) -> list[tuple[Entity, str]]:
        def get_criteria(entity):
            return ratings.filters(entity_name=entity.name).keys("criterion") \
                | comparisons.filters(left_name=entity.name).keys("criterion") \
                | comparisons.filters(right_name=entity.name).keys("criterion")
        return [(entity, str(criterion)) for entity in entities for criterion in get_criteria(entity)]
    
    def _nonargs_list(self, # type: ignore
        variables: list[tuple[Entity, str]],
        users: Users, 
        ratings: Ratings, # keynames == ["entity_name", "criterion", "username"]
        comparisons: Comparisons, # keynames == ["entity_name", "criterion", "username", "other_name"]
    ) -> list[Users]:
        """ Returns a list of evaluators, for each variable """
        users_list: list[Users] = list()
        for entity, criterion in variables:
            usernames = ratings.filters(entity_name=entity.name, criterion=criterion).keys("username")
            usernames |= comparisons.filters(left_name=entity.name, criterion=criterion).keys("username")
            usernames |= comparisons.filters(right_name=entity.name, criterion=criterion).keys("username")
            users_subset = users[list(usernames)]
            assert isinstance(users_subset, Users)
            users_list.append(users_subset)
        return users_list
    
    def _args(self, # type: ignore
        variable: tuple[Entity, str],
        nonargs, # evaluators: Users
        public_settings: PublicSettings, # set(keynames) == {"username", "entity_name"}
    ) -> tuple[NDArray, NDArray, float, float]:
        (entity, _), evaluators = variable, nonargs
        assert isinstance(evaluators, Users)
        trusts = np.array([user["trust"] for user in evaluators])
        public = np.array([public_settings.get(username=user.name, entity_name=entity.name)["public"] for user in evaluators])
        privacy_weights = public * (1 - self.privacy_penalty) + self.privacy_penalty
        return trusts, privacy_weights, self.overtrust_ratio, self.min_overtrust

    def thread_function(self,
        trusts: NDArray,
        privacy_weights: NDArray,
        overtrust_ratio: float,
        min_overtrust: float,
    ) -> tuple[NDArray, tuple[float, float, float]]:
        """ Computes voting rights and statistics without having to care about usernames """
        cumulative_trust = (trusts * privacy_weights).sum()
        max_overtrust = cumulative_trust * overtrust_ratio + min_overtrust
        min_voting_right = AffineOvertrust.min_voting_right(max_overtrust, trusts, privacy_weights)
        voting_rights = privacy_weights * trusts.clip(min=min_voting_right)
        return voting_rights, (cumulative_trust, min_voting_right, voting_rights.sum() - cumulative_trust)

    @staticmethod
    def min_voting_right(max_overtrust: float, trusts: NDArray, privacy_weights: NDArray) -> float:
        """ Returns the minimal voting rights that corresponds to max_overtrust """
        assert max_overtrust >= 0
        if AffineOvertrust.overtrust(1.0, trusts, privacy_weights) <= max_overtrust:
            return 1.
        return solve(AffineOvertrust.overtrust, max_overtrust, 0, 1, args=(trusts, privacy_weights)) # type: ignore

    @staticmethod
    def overtrust(min_voting_right: float, trusts: NDArray, privacy_weights: NDArray) -> float:
        return (privacy_weights * (min_voting_right - trusts))[min_voting_right > trusts].sum()

    def _process_results(self,  # type: ignore
        variables: list[tuple[Entity, str]], 
        nonargs_list: list[tuple[Users]], # evaluators_list
        results: list[tuple[NDArray, tuple[float, float, float]]], 
        args_lists: list, # not used
        entities: Entities,
    ) -> tuple[Entities, VotingRights]:
        entities, voting_rights = deepcopy(entities), VotingRights()
        stat_names = ("cumulative_trust", "min_voting_right", "overtrust")
        for (entity, criterion), evaluators, (vrights, statistics) in zip(variables, nonargs_list, results):
            for user, voting_right in zip(evaluators, vrights):
                voting_rights.set(username=user.name, entity=entity.name, criterion=criterion, voting_right=voting_right)
            for name, stat in zip(stat_names, statistics):
                entity[f"{criterion}_{name}"] = stat
        return entities, voting_rights