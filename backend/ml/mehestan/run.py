import logging
import os
from functools import partial
from multiprocessing import Pool

import pandas as pd
from django import db
from django.conf import settings
from solidago import collaborative_scaling
from solidago.pipeline import TournesolInput, PipelineParameters
from solidago.pipeline.individual_scores import get_individual_scores

from core.models import User
from ml.inputs import MlInputFromDb
from ml.outputs import (
    save_contributor_scalings,
    save_contributor_scores,
    save_entity_scores,
    save_tournesol_scores,
)
from tournesol.models import Poll
from tournesol.models.entity_score import ScoreMode
from tournesol.utils.constants import COMPARISON_MAX
from vouch.voting_rights import compute_voting_rights

from .global_scores import get_global_scores

logger = logging.getLogger(__name__)

VOTE_WEIGHT_PUBLIC_RATINGS = 1.0
VOTE_WEIGHT_PRIVATE_RATINGS = 0.5


class MehestanParameters(PipelineParameters):
    r_max = COMPARISON_MAX



def update_user_scores(poll: Poll, user: User):
    params = MehestanParameters()
    ml_input = MlInputFromDb(poll_name=poll.name)
    for criteria in poll.criterias_list:
        scores = get_individual_scores(
            ml_input,
            criteria,
            parameters=params,
            single_user_id=user.pk,
        )
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
        # trust score would be possibly None (NULL) when new users are created and when
        # computation of trust scores fail for any reason (e.g. no user pre-trusted)
        ratings_df.trust_score.fillna(0.0, inplace=True)
        for (_, ratings_group) in ratings_df.groupby("entity_id"):
            ratings_df.loc[ratings_group.index, "voting_right"] = compute_voting_rights(
                ratings_group.trust_score.to_numpy(), ratings_group.privacy_penalty.to_numpy()
            )
    return ratings_df


def run_mehestan_for_criterion(
    criteria: str,
    ml_input: TournesolInput,
    poll_pk: int,
    parameters: MehestanParameters
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

    indiv_scores = get_individual_scores(ml_input, criteria=criteria, parameters=parameters)

    logger.info("Individual scores computed for crit '%s'", criteria)
    scalings = collaborative_scaling.compute_individual_scalings(
        individual_scores=indiv_scores,
        tournesol_input=ml_input,
        W=parameters.W,
    )
    scaled_scores = collaborative_scaling.apply_scalings(
        individual_scores=indiv_scores,
        scalings=scalings
    )

    if len(scaled_scores) > 0:
        score_shift = collaborative_scaling.estimate_positive_score_shift(
            scaled_scores,
            W=parameters.score_shift_W,
            quantile=parameters.score_shift_quantile,
        )
        score_std = collaborative_scaling.estimate_score_deviation(
            scaled_scores,
            W=parameters.score_shift_W,
            quantile=parameters.score_deviation_quantile,
        )
        scaled_scores.score -= score_shift
        scaled_scores.score /= score_std
        scaled_scores.uncertainty /= score_std

    indiv_scores["criteria"] = criteria
    save_contributor_scalings(poll, criteria, scalings)

    # Join ratings columns ("is_public", "trust_score", etc.)
    ratings = ml_input.ratings_properties.set_index(["user_id", "entity_id"])
    scaled_scores = scaled_scores.join(
        ratings,
        on=["user_id", "entity_id"],
    )

    scaled_scores_with_voting_rights_per_score_mode = {
        mode: add_voting_rights(scaled_scores, score_mode=mode) for mode in ScoreMode
    }
    for mode in ScoreMode:
        scaled_scores_with_voting_rights = scaled_scores_with_voting_rights_per_score_mode[mode]
        global_scores = get_global_scores(scaled_scores_with_voting_rights, W=parameters.W)
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


def run_mehestan(
    ml_input: TournesolInput,
    poll: Poll,
    parameters: MehestanParameters,
    main_criterion_only=False
):
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

    criteria_to_run = [poll.main_criteria]
    if not main_criterion_only:
        criteria_to_run.extend(c for c in criteria if c != poll.main_criteria)

    # compute each criterion in parallel
    cpu_count = os.cpu_count() or 1
    cpu_count -= settings.MEHESTAN_KEEP_N_FREE_CPU

    with Pool(processes=max(1, cpu_count)) as pool:
        for _ in pool.imap_unordered(
            partial(
                run_mehestan_for_criterion,
                ml_input=ml_input,
                poll_pk=poll_pk,
                parameters=parameters
            ),
            criteria_to_run,
        ):
            pass

    save_tournesol_scores(poll)
    logger.info("Mehestan for poll '%s': Done", poll.name)
