import logging
import os
from functools import partial
from multiprocessing import Pool
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

logger = logging.getLogger(__name__)


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
    logger.debug("Individual scores computed for crit '%s'", criteria)
    global_scores, scalings = get_global_scores(
        ml_input, individual_scores=indiv_scores
    )
    logger.debug("Global scores computed for crit '%s'", criteria)
    indiv_scores["criteria"] = criteria
    global_scores["criteria"] = criteria
    return indiv_scores, global_scores, scalings


def update_user_scores(poll: Poll, user: User):
    ml_input = MlInputFromDb(poll_name=poll.name)
    for criteria in poll.criterias_list:
        scores = get_individual_scores(ml_input, criteria, single_user_id=user.pk)
        scores["criteria"] = criteria
        save_contributor_scores(
            poll, scores, single_criteria=criteria, single_user_id=user.pk
        )


def _run_mehestan_for_criterion(criteria: str, ml_input: MlInput, poll_pk: int):
    poll = Poll.objects.get(pk=poll_pk)
    logger.info(
        "Mehestan for poll '%s': computing scores for crit '%s'",
        poll.name,
        criteria,
    )
    indiv_scores, global_scores, _ = compute_mehestan_scores(
        ml_input, criteria=criteria
    )
    logger.info(
        "Mehestan for poll '%s': scores computed for crit '%s'",
        poll.name,
        criteria,
    )
    save_contributor_scores(poll, indiv_scores, single_criteria=criteria)
    save_entity_scores(poll, global_scores, single_criteria=criteria)
    logger.info(
        "Mehestan for poll '%s': scores saved for crit '%s'",
        poll.name,
        criteria,
    )


def run_mehestan(ml_input: MlInput, poll: Poll):
    logger.info("Mehestan for poll '%s': Start", poll.name)

    # This function use multiprocessing
    #
    # Thus the model instances used by the child processes must be passed from
    # the parent process. Child processes must retrieve the objects using
    # their own database connection.
    poll_pk = poll.pk
    criteria = poll.criterias_list

    from django import db

    os.register_at_fork(before=db.connections.close_all)

    # compute each criterion in parallel
    with Pool(processes=os.cpu_count() - 1) as pool:
        for i in pool.imap_unordered(
            partial(_run_mehestan_for_criterion, ml_input=ml_input, poll_pk=poll_pk),
            criteria,
        ):
            pass

    save_tournesol_score_as_sum_of_criteria(poll)
    logger.info("Mehestan for poll '%s': Done", poll.name)
