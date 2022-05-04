import logging
import os
from functools import partial
from multiprocessing import Pool
from typing import Optional

import pandas as pd
from django import db

from core.models import User
from ml.inputs import MlInput, MlInputFromDb
from ml.outputs import (
    save_contributor_scalings,
    save_contributor_scores,
    save_entity_scores,
    save_tournesol_score_as_sum_of_criteria,
)
from tournesol.models import Poll
from tournesol.models.entity_score import ScoreMode

from .global_scores import compute_scaled_scores, get_global_scores
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


def update_user_scores(poll: Poll, user: User):
    ml_input = MlInputFromDb(poll_name=poll.name)
    for criteria in poll.criterias_list:
        scores = get_individual_scores(ml_input, criteria, single_user_id=user.pk)
        scores["criteria"] = criteria
        save_contributor_scores(
            poll, scores, single_criteria=criteria, single_user_id=user.pk
        )


def _run_mehestan_for_criterion(criteria: str, ml_input: MlInput, poll_pk: int):
    """
    Run Mehestan for the given criterion, in the given poll.
    """
    # Retrieving the poll instance here allows this function to be run in a
    # forked process. See the function `run_mehestan`.
    poll = Poll.objects.get(pk=poll_pk)
    logger.info(
        "Mehestan for poll '%s': computing scores for crit '%s'",
        poll.name,
        criteria,
    )

    indiv_scores = get_individual_scores(ml_input, criteria=criteria)
    logger.debug("Individual scores computed for crit '%s'", criteria)
    scaled_scores, scalings = compute_scaled_scores(
        ml_input, individual_scores=indiv_scores
    )

    indiv_scores["criteria"] = criteria
    save_contributor_scalings(poll, criteria, scalings)
    save_contributor_scores(poll, indiv_scores, single_criteria=criteria)

    for mode in ScoreMode:
        global_scores = get_global_scores(scaled_scores, score_mode=mode)
        global_scores["criteria"] = criteria

        logger.info(
            "Mehestan for poll '%s': scores computed for crit '%s' and mode '%s'",
            poll.name,
            criteria,
            mode,
        )
        save_entity_scores(poll, global_scores, single_criteria=criteria, score_mode=mode)

    logger.info(
        "Mehestan for poll '%s': done with crit '%s'",
        poll.name,
        criteria,
    )


def run_mehestan(ml_input: MlInput, poll: Poll):
    """
    This function use multiprocessing.

        1. Always close all database connections in the main process before
           creating forks. Django will automatically re-create new database
           connections when needed.

        2. Do not pass Django model's instances as arguments to the function
           run by child processes. Using such instances in child processes
           will raise an exception: connection already closed.

        3. Do not fork the main process within a code block managed by
           a single database transaction.

    See the indications to close the database connections:
        - https://www.psycopg.org/docs/usage.html#thread-and-process-safety
        - https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNECT

    See how django handles database connections:
        - https://docs.djangoproject.com/en/4.0/ref/databases/#connection-management
    """
    logger.info("Mehestan for poll '%s': Start", poll.name)

    # Avoid passing model's instances as arguments to the function run by the
    # child processes. See this method docstring.
    poll_pk = poll.pk
    criteria = poll.criterias_list

    os.register_at_fork(before=db.connections.close_all)

    # compute each criterion in parallel
    with Pool(processes=max(1, os.cpu_count() - 1)) as pool:
        for _ in pool.imap_unordered(
            partial(_run_mehestan_for_criterion, ml_input=ml_input, poll_pk=poll_pk),
            criteria,
        ):
            pass

    save_tournesol_score_as_sum_of_criteria(poll)
    logger.info("Mehestan for poll '%s': Done", poll.name)
