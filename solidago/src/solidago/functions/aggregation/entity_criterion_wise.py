from functools import reduce
import operator

import numpy as np
from numpy.typing import NDArray

from solidago.poll import *
from solidago.functions.threaded import ThreadedPollFunction


class EntityCriterionWise(ThreadedPollFunction):
    note: str="entity_criterion_wise_aggregation"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _variables(self, entities: Entities, user_models: UserModels) -> list[tuple[Entity, str]]: # type: ignore
        return [(e, c) for e in entities for c in user_models.criteria()]

    def _nonargs_list(self,  # type: ignore
        variables: list[tuple[Entity, str]], 
        entities: Entities,
        user_models: UserModels,
    ) -> list[Scores]:
        with self.timeit(f"{type(self).__name__} - Loading data - Nonargs - user_models", unit="ms"):
            scores = user_models(entities)
        return [scores.filters(entity_name=e.name, criterion=c) for e, c in variables]

    def _args(self, # type: ignore
        variable: tuple[Entity, str], 
        nonargs, # score: Scores, with keynames == {"username"}
        voting_rights: VotingRights,
    ) -> tuple[NDArray, NDArray, NDArray, NDArray]:
        assert isinstance(nonargs, Scores) and "username" in nonargs.keynames, nonargs
        (entity, criterion), scores = variable, nonargs
        voting_rights_df = voting_rights.df
        filters = []
        if "entity_name" in voting_rights.keynames:
            filters.append(voting_rights_df["entity_name"] == entity.name)
        if "criterion" in voting_rights.keynames:
            filters.append(voting_rights_df["criterion"] == criterion)
        if filters:
            mask = reduce(operator.__and__, filters)
            voting_rights_df = voting_rights_df[mask]
        voting_right_by_username = dict(zip(voting_rights_df["username"], voting_rights_df["voting_right"]))
        vrights = [
            voting_right_by_username.get(username, 0.)
            for username in scores("username")
        ]
        values, left_uncs, right_uncs = scores.value, scores.left_unc, scores.right_unc
        return np.array(vrights, dtype=np.float64), values, left_uncs, right_uncs

    def _process_results(self,  # type: ignore
        variables: list[tuple[Entity, str]], 
        nonargs_list: list, 
        results: list, args_lists: list
    ) -> ScoringModel: # type: ignore
        rows = [
            (entity.name, criterion, value, left, right)
            for (entity, criterion), (value, left, right) in zip(variables, results)
        ]
        directs = DirectScores(rows, columns=["entity_name", "criterion", "value", "left_unc", "right_unc"])
        return ScoringModel(directs=directs, note=self.note)
    