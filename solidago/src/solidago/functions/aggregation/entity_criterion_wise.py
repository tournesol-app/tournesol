import numpy as np
from numpy.typing import NDArray

from solidago.poll import *
from solidago.functions.parallelized import ParallelizedPollFunction


class EntityCriterionWise(ParallelizedPollFunction):
    note: str="entity_criterion_wise_aggregation"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _variables(self, entities: Entities, user_models: UserModels) -> list[tuple[Entity, str]]:
        return [(entity, criterion) for entity in entities for criterion in user_models.criteria()]

    def _nonargs_list(self, 
        variables: list, 
        entities: Entities,
        user_models: UserModels,
    ) -> list[MultiScore]:
        scores = user_models(entities).reorder("entity_name", "criterion", "username")
        return [scores[entity, criterion] for entity, criterion in variables]

    def _args(self,
        variable: tuple[Entity, str], 
        nonargs, # score: MultiScore, with keynames == ["username"]
        voting_rights: VotingRights,
    ) -> tuple[NDArray, NDArray, NDArray, NDArray]:
        assert isinstance(nonargs, MultiScore) and nonargs.keynames == ("username",), nonargs
        (entity, criterion), scores = variable, nonargs
        vrights, values, lefts, rights = list(), list(), list(), list()
        for (username,), score in scores:
            assert isinstance(score, Score)
            vrights.append(voting_rights.get(username=username, entity_name=entity, criterion=criterion))
            values.append(score.value)
            lefts.append(score.left_unc)
            rights.append(score.right_unc)
        return tuple(np.array(x, dtype=np.float64) for x in (vrights, values, lefts, rights))

    def _process_results(self, variables: list, nonargs_list: list, results: list, args_lists: list) -> ScoringModel:
        global_model = ScoringModel(note=type(self).note)
        for (entity_name, criterion), (value, left, right) in zip(variables, results):
            global_model.directs[entity_name, criterion] = Score(value, left, right)
        return global_model
    