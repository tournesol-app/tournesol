import logging
import os
from functools import partial
from math import tau as TAU
from multiprocessing import Pool
from typing import Optional

import numpy as np
import pandas as pd
from django import db
from solidago.collaborative_scaling import estimate_positive_score_shift, estimate_score_std
from solidago.comparisons_to_scores import ContinuousBradleyTerry

from core.models import User
from ml.inputs import MlInput, MlInputFromDb
from ml.outputs import (
    save_contributor_scalings,
    save_contributor_scores,
    save_entity_scores,
    save_tournesol_scores,
)
from tournesol.models import Poll
from tournesol.models.entity_score import ScoreMode
from tournesol.utils.constants import COMPARISON_MAX, MEHESTAN_MAX_SCALED_SCORE
from vouch.voting_rights import compute_voting_rights

from .global_scores import compute_scaled_scores, get_global_scores

logger = logging.getLogger(__name__)

VOTE_WEIGHT_PUBLIC_RATINGS = 1.0
VOTE_WEIGHT_PRIVATE_RATINGS = 0.5

SCORE_SHIFT_W = 1.
SCORE_SHIFT_QUANTILE = 0.15  # TODO maybe use 5% ?

individual_scores_algo = ContinuousBradleyTerry(r_max=COMPARISON_MAX)


def get_individual_scores(
    ml_input: MlInput, criteria: str, single_user_id: Optional[int] = None
) -> pd.DataFrame:
    comparisons_df = ml_input.get_comparisons(criteria=criteria, user_id=single_user_id)
    initial_contributor_scores = ml_input.get_individual_scores(
        criteria=criteria, user_id=single_user_id
    )
    if initial_contributor_scores is not None:
        initial_contributor_scores = initial_contributor_scores.groupby("user_id")

    individual_scores = []
    for (user_id, user_comparisons) in comparisons_df.groupby("user_id"):
        if initial_contributor_scores is None:
            initial_entity_scores = None
        else:
            try:
                contributor_score_df = initial_contributor_scores.get_group(user_id)
                initial_entity_scores = pd.Series(
                    data=contributor_score_df.raw_score,
                    index=contributor_score_df.entity
                )
            except KeyError:
                initial_entity_scores = None
        scores = individual_scores_algo.compute_individual_scores(
            user_comparisons, initial_entity_scores=initial_entity_scores
        )
        if scores is None:
            continue
        scores["user_id"] = user_id
        individual_scores.append(scores.reset_index())

    if len(individual_scores) == 0:
        return pd.DataFrame(columns=["user_id", "entity_id", "raw_score", "raw_uncertainty"])

    result = pd.concat(individual_scores, ignore_index=True, copy=False)
    return result.reindex(columns=["user_id", "entity_id", "raw_score", "raw_uncertainty"])


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
        save_contributor_scores(poll, scores, single_criteria=criteria, single_user_id=user.pk)


def add_voting_rights(ratings_properties_df: pd.DataFrame, score_mode=ScoreMode.DEFAULT):
    """
    Add a "voting_right" column to the ratings_df DataFrame

    Parameters
    ----------
    - ratings_properties_df:
        DataFrame of ratings. All ratings must be on the same criteria and the df must have
        columns: user_id, entity_id, trust_score, is_public
    """
    ratings_df = ratings_properties_df.copy(deep=True)
    ratings_df["voting_right"] = 0.0
    ratings_df["privacy_penalty"] = ratings_df.is_public.map(
        {
            True: VOTE_WEIGHT_PUBLIC_RATINGS,
            False: VOTE_WEIGHT_PRIVATE_RATINGS,
        }
    )
    if score_mode == ScoreMode.TRUSTED_ONLY:
        ratings_df = ratings_df[ratings_df["trust_score"] >= 0.8]
        ratings_df["voting_right"] = 1
    if score_mode == ScoreMode.ALL_EQUAL:
        ratings_df["voting_right"] = 1
    if score_mode == ScoreMode.DEFAULT:
        for (_, ratings_group) in ratings_df.groupby("entity_id"):
            # trust score would be possibly None (NULL) when new users are created and when
            # computation of trust scores fail for any reason (e.g. no user pre-trusted)
            ratings_group.trust_score.fillna(0.0, inplace=True)
            ratings_df.loc[ratings_group.index, "voting_right"] = compute_voting_rights(
                ratings_group.trust_score.to_numpy(), ratings_group.privacy_penalty.to_numpy()
            )
    return ratings_df


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
    scaled_scores, scalings = compute_scaled_scores(ml_input, individual_scores=indiv_scores)
    score_shift = estimate_positive_score_shift(
        scaled_scores,
        SCORE_SHIFT_W,
        SCORE_SHIFT_QUANTILE,
    )
    score_std = estimate_score_std(
        scaled_scores,
        SCORE_SHIFT_W,
    )
    score_std_np = np.std(scaled_scores.score)

    print("-- scaled_scores --\n", scaled_scores.score.describe())
    print("tail:\n", scaled_scores.tail(20))

    scaled_scores.score -= score_shift
    scaled_scores.score /= score_std_np
    scaled_scores.uncertainty /= score_std_np

    print("STD", score_std)
    print("SHIFT", score_shift)
    print("NEW STD", np.std(scaled_scores.score))

    print("-- scaled_scores after shift --\n", scaled_scores.score.describe())
    print("tail:\n", scaled_scores.tail(20))


    indiv_scores["criteria"] = criteria
    save_contributor_scalings(poll, criteria, scalings)

    scaled_scores_with_voting_rights_per_score_mode = {
        mode: add_voting_rights(scaled_scores, score_mode=mode) for mode in ScoreMode
    }
    for mode in ScoreMode:
        scaled_scores_with_voting_rights = scaled_scores_with_voting_rights_per_score_mode[mode]
        global_scores = get_global_scores(scaled_scores_with_voting_rights)
        global_scores["criteria"] = criteria

        # Apply poll scaling
        scale_function = poll.scale_function
        global_scores["uncertainty"] = 0.5 * (
            scale_function(global_scores["score"] + global_scores["uncertainty"])
            - scale_function(global_scores["score"] - global_scores["uncertainty"])
        )
        global_scores["score"] = scale_function(global_scores["score"])

        # 2023-05-20: deviation is no longer computed by Mehestan
        global_scores["deviation"] = None

        logger.info(
            "Mehestan for poll '%s': scores computed for crit '%s' and mode '%s'",
            poll.name,
            criteria,
            mode,
        )
        save_entity_scores(poll, global_scores, single_criteria=criteria, score_mode=mode)

    scale_function = poll.scale_function
    scaled_scores = scaled_scores_with_voting_rights_per_score_mode[ScoreMode.DEFAULT]
    scaled_scores["uncertainty"] = 0.5 * (
        scale_function(scaled_scores["score"] + scaled_scores["uncertainty"])
        - scale_function(scaled_scores["score"] - scaled_scores["uncertainty"])
    )
    scaled_scores["score"] = scale_function(scaled_scores["score"])
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
