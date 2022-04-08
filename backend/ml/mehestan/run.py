from typing import Optional

import pandas as pd

from core.models import User
from ml.inputs import MlInput, MlInputFromDb
from ml.outputs import (
    save_contributor_scores,
    save_entity_scores,
    save_tournesol_score_as_sum_of_criteria,
)
from tournesol.models import Poll

from .global_scores import get_global_scores
from .individual import compute_individual_score


def get_individual_scores(
    ml_input: MlInput, criteria: str, single_user_id: Optional[int] = None
) -> pd.DataFrame:
    comparisons_df = ml_input.get_comparisons(criteria=criteria, user_id=single_user_id)

    individual_scores = []
    for (user_id, user_comparisons) in comparisons_df.groupby("user_id"):
        scores = compute_individual_score(user_comparisons)
        if scores is None:
            continue
        scores["user_id"] = user_id
        individual_scores.append(scores.reset_index())

    if len(individual_scores) == 0:
        return pd.DataFrame(columns=["user_id", "entity_id", "score", "uncertainty"])

    result = pd.concat(individual_scores, ignore_index=True, copy=False)
    return result[["user_id", "entity_id", "score", "uncertainty"]]


def compute_mehestan_scores(ml_input, criteria):
    indiv_scores = get_individual_scores(ml_input, criteria=criteria)
    indiv_scores["criteria"] = criteria
    global_scores, scalings = get_global_scores(
        ml_input, individual_scores=indiv_scores
    )
    global_scores["criteria"] = criteria
    return indiv_scores, global_scores, scalings


def update_user_scores(poll: Poll, user: User):
    ml_input = MlInputFromDb(poll_name=poll.name)
    for criteria in poll.criterias_list:
        scores = get_individual_scores(ml_input, criteria, single_user_id=user.pk)
        scores["criteria"] = criteria
        save_contributor_scores(poll, scores, single_criteria=criteria, single_user_id=user.pk)


def run_mehestan(ml_input: MlInput, poll: Poll):
    for criteria in poll.criterias_list:
        indiv_scores, global_scores, _ = compute_mehestan_scores(
            ml_input, criteria=criteria
        )
        save_contributor_scores(poll, indiv_scores, single_criteria=criteria)
        save_entity_scores(poll, global_scores, single_criteria=criteria)
    save_tournesol_score_as_sum_of_criteria(poll)
