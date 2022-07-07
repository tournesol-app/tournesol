import logging
import os
from functools import partial
from math import tau as TAU
from multiprocessing import Pool
from typing import Optional

import numpy as np
import pandas as pd
from django import db

from core.models.user import User
from ml.inputs import MlInput, MlInputFromDb
from ml.outputs import (
    save_contributor_scalings,
    save_contributor_scores,
    save_entity_scores,
    save_tournesol_scores,
)
from tournesol.models import Poll
from tournesol.models.entity_score import ScoreMode
from tournesol.utils.constants import MEHESTAN_MAX_SCALED_SCORE

from .global_scores import compute_scaled_scores, get_global_scores
from .individual import compute_individual_score

logger = logging.getLogger(__name__)

MAX_SCORE = MEHESTAN_MAX_SCALED_SCORE
POLL_SCALING_QUANTILE = 0.99
POLL_SCALING_SCORE_AT_QUANTILE = 50.0


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
        scores.rename(
            columns={
                "score": "raw_score",
                "uncertainty": "raw_uncertainty",
            },
            inplace=True,
        )
        save_contributor_scores(
            poll, scores, single_criteria=criteria, single_user_id=user.pk
        )


def run_mehestan_for_criterion(
    criteria: str,
    ml_input: MlInput,
    poll_pk: int,
    update_poll_scaling=False,
):
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

    for mode in ScoreMode:
        global_scores = get_global_scores(scaled_scores, score_mode=mode)
        global_scores["criteria"] = criteria

        if update_poll_scaling and mode == ScoreMode.DEFAULT:
            quantile_value = np.quantile(global_scores["score"], POLL_SCALING_QUANTILE)
            scale = (
                np.tan(POLL_SCALING_SCORE_AT_QUANTILE * TAU / (4 * MAX_SCORE))
                / quantile_value
            )
            poll.sigmoid_scale = scale
            poll.save(update_fields=["sigmoid_scale"])

        # Apply poll scaling
        scale_function = poll.scale_function
        global_scores["uncertainty"] = 0.5 * (
            scale_function(global_scores["score"] + global_scores["uncertainty"])
            - scale_function(global_scores["score"] - global_scores["uncertainty"])
        )
        global_scores["deviation"] = 0.5 * (
            scale_function(global_scores["score"] + global_scores["deviation"])
            - scale_function(global_scores["score"] - global_scores["deviation"])
        )
        global_scores["score"] = scale_function(global_scores["score"])

        logger.info(
            "Mehestan for poll '%s': scores computed for crit '%s' and mode '%s'",
            poll.name,
            criteria,
            mode,
        )
        save_entity_scores(
            poll, global_scores, single_criteria=criteria, score_mode=mode
        )

    scale_function = poll.scale_function
    scaled_scores["raw_score"] = scaled_scores["score"]
    scaled_scores["raw_uncertainty"] = scaled_scores["uncertainty"]
    scaled_scores["uncertainty"] = 0.5 * (
        scale_function(scaled_scores["raw_score"] + scaled_scores["raw_uncertainty"])
        - scale_function(scaled_scores["raw_score"] - scaled_scores["raw_uncertainty"])
    )
    scaled_scores["score"] = scale_function(scaled_scores["raw_score"])
    scaled_scores["criteria"] = criteria
    save_contributor_scores(poll, scaled_scores, single_criteria=criteria)

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

    # Run Mehestan for main criterion:
    # Global scores for other criteria will use the poll scaling computed
    # based on this criterion. That's why it needs to run first, before other
    # criteria can be parallelized.
    run_mehestan_for_criterion(
        ml_input=ml_input,
        poll_pk=poll_pk,
        criteria=poll.main_criteria,
        update_poll_scaling=True,
    )

    # compute each criterion in parallel
    remaining_criteria = [c for c in criteria if c != poll.main_criteria]
    cpu_count = os.cpu_count() or 1
    with Pool(processes=max(1, cpu_count - 1)) as pool:
        for _ in pool.imap_unordered(
            partial(run_mehestan_for_criterion, ml_input=ml_input, poll_pk=poll_pk),
            remaining_criteria,
        ):
            pass

    save_tournesol_scores(poll)
    logger.info("Mehestan for poll '%s': Done", poll.name)
