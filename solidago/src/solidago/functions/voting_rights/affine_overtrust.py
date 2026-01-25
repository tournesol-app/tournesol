from numpy.typing import NDArray

import numpy as np

from solidago.primitives.dichotomy import solve
from solidago.poll import *
from solidago.functions.parallelized import ParallelizedPollFunction


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

    def _process_kwargs(self, assessments: Assessments, comparisons: Comparisons) -> dict:
        return dict(
            assessments=assessments.reorder("entity_name", "criterion", "username"),
            comparisons=comparisons.reorder("entity_name", "criterion", "username", "other_name"),
        )
    
    def _variables(self,
        entities: Entities, 
        assessments: Assessments, # keynames == ["entity_name", "criterion", "username"]
        comparisons: Comparisons, # keynames == ["entity_name", "criterion", "username", "other_name"]
    ) -> list[tuple[Entity, str]]:
        def get_criteria(e):
            return assessments[e].keys("criterion") | comparisons[e].keys("criterion")
        return [(entity, criterion) for entity in entities for criterion in get_criteria(entity)]
    
    def _nonargs_list(self,
        variables: list[tuple[Entity, str]],
        users: Users, 
        assessments: Assessments, # keynames == ["entity_name", "criterion", "username"]
        comparisons: Comparisons, # keynames == ["entity_name", "criterion", "username", "other_name"]
    ) -> list[Users]:
        """ Returns a list of evaluators, for each variable """
        return [
            users[assessments[e, c].keys("username") | comparisons[e, c].keys("username")]
            for e, c in variables
        ]
    
    def _args(self,
        variable: tuple[Entity, str],
        nonargs, # evaluators: Users
        made_public: MadePublic, # set(keynames) == {"username", "entity_name"}
    ) -> tuple[NDArray, NDArray, float, float]:
        (entity, _), evaluators = variable, nonargs
        trusts = np.array([user.trust if hasattr(user, "trust") else 0.0 for user in evaluators])
        public = np.array([made_public.get(username=user, entity_name=entity) for user in evaluators])
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

    def min_voting_right(max_overtrust: float, trusts: NDArray, privacy_weights: NDArray) -> float:
        """ Returns the minimal voting rights that corresponds to max_overtrust """
        assert max_overtrust >= 0
        if AffineOvertrust.overtrust(1.0, trusts, privacy_weights) <= max_overtrust:
            return 1.
        return solve(AffineOvertrust.overtrust, max_overtrust, 0, 1, args=(trusts, privacy_weights))

    def overtrust(min_voting_right: float, trusts: NDArray, privacy_weights: NDArray) -> float:
        return (privacy_weights * (min_voting_right - trusts))[min_voting_right > trusts].sum()

    def _process_results(self, 
        variables: list[tuple[Entity, str]], 
        nonargs_list: list[tuple[Users]], # evaluators_list
        results: list[tuple[NDArray, tuple[float, float, float]]], 
        args_lists: list, # not used
        entities: Entities,
    ) -> tuple[Entities, VotingRights]:
        entities, voting_rights = entities.deepcopy(), VotingRights()
        stat_names = ("cumulative_trust", "min_voting_right", "overtrust")
        for (entity, criterion), evaluators, (vrights, statistics) in zip(variables, nonargs_list, results):
            for user, voting_right in zip(evaluators, vrights):
                voting_rights[user, entity, criterion] = voting_right
            for name, stat in zip(stat_names, statistics):
                entities[str(entity)][f"{criterion}_{name}"] = stat
        return entities, voting_rights