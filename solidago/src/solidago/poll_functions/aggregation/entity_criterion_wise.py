import numpy as np
from numpy.typing import NDArray

from solidago.poll import *
from solidago.poll_functions.parallelized import ParallelizedPollFunction


class EntityCriterionWise(ParallelizedPollFunction):
    note: str="entity_criterion_wise_aggregation"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _variables(self, entities: Entities, user_models: UserModels) -> list[tuple[Entity, str]]: # type: ignore
        return [(entity, criterion) for entity in entities for criterion in user_models.criteria()]

    def _nonargs_list(self,  # type: ignore
        variables: list[tuple[Entity, str]], 
        entities: Entities,
        user_models: UserModels,
    ) -> list[Scores]:
        scores = user_models(entities)
        return [scores.filters(entity_name=e.name, criterion=c) for e, c in variables]

    def _args(self, # type: ignore
        variable: tuple[Entity, str], 
        nonargs, # score: Scores, with keynames == {"username"}
        voting_rights: VotingRights,
    ) -> tuple[NDArray, NDArray, NDArray, NDArray]:
        assert isinstance(nonargs, Scores) and "username" in nonargs.keynames, nonargs
        (entity, criterion), scores = variable, nonargs
        vrights = list()
        for score in scores:
            assert isinstance(score, Score)
            kwargs = dict(username=score["username"], entity_name=entity.name, criterion=criterion)
            vright = voting_rights.get(**kwargs)["voting_right"]
            vrights.append(vright)
        values, left_uncs, right_uncs = scores.value, scores.left_unc, scores.right_unc
        return np.array(vrights, dtype=np.float64), values, left_uncs, right_uncs

    def _process_results(self,  # type: ignore
        variables: list[tuple[Entity, str]], 
        nonargs_list: list, 
        results: list, args_lists: list
    ) -> ScoringModel: # type: ignore
        global_model = ScoringModel(note=type(self).note)
        for (entity, criterion), (value, left, right) in zip(variables, results):
            score = Score((value, left, right))
            global_model.directs.set(score, entity_name=entity.name, criterion=criterion)
        return global_model
    