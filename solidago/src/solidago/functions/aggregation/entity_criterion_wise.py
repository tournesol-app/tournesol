from abc import abstractmethod

import numpy as np

from solidago.poll import *
from solidago.functions.parallelized import ParallelizedPollFunction
from solidago.primitives.threading import threading
from solidago.primitives.timer import time


class EntityCriterionWise(ParallelizedPollFunction):
    note: str="entity_criterion_wise_aggregation"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _variables(self, entities: Entities, user_models: UserModels) -> list[tuple[Entity, str]]:
        return [(entity, criterion) for entity in entities for criterion in user_models.criteria()]
    
    def _args(self,
        variable: tuple[Entity, str], 
        voting_rights: VotingRights,
        user_models: UserModels,
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        entity, criterion = variable
        vrights, values, lefts, rights = list(), list(), list(), list()
        for (username,), score in user_models(entity, criterion):
            assert isinstance(score, Score)
            vrights.append(voting_rights.get(username=username, entity_name=entity, criterion=criterion))
            values.append(score.value)
            lefts.append(score.left_unc)
            rights.append(score.right_unc)
        def f(array):
            return np.array(array, dtype=np.float64)
        return f(vrights), f(values), f(lefts), f(rights)

    def _process_results(self, variables: list, nonargs_list: list, results: list, *args_lists) -> ScoringModel:
        global_model = ScoringModel(note=type(self).note)
        for (entity_name, criterion), (value, left, right) in zip(variables, results):
            global_model[entity_name, criterion] = Score(value, left, right)
        return global_model
    