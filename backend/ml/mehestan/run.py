import logging
import os
from functools import partial
from multiprocessing import Pool

import pandas as pd
from django import db
from django.conf import settings
from solidago import collaborative_scaling
from solidago.pipeline import PipelineOutput, PipelineParameters, TournesolInput
from solidago.pipeline.global_scores import aggregate_scores, get_squash_function
from solidago.pipeline.individual_scores import get_individual_scores

from core.models import User
from ml.inputs import MlInputFromDb
from ml.outputs import TournesolPollOutput, save_tournesol_scores
from tournesol.models import Poll
from tournesol.models.entity_score import ScoreMode
from vouch.voting_rights import compute_voting_rights

from .parameters import MehestanParameters

logger = logging.getLogger(__name__)

VOTE_WEIGHT_PUBLIC_RATINGS = 1.0
VOTE_WEIGHT_PRIVATE_RATINGS = 0.5


def update_user_scores(poll: Poll, user: User):
    params = MehestanParameters()
    ml_input = MlInputFromDb(poll_name=poll.name)
    output = TournesolPollOutput(poll_name=poll.name)
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
        output.save_individual_scores(
            scores,
            criterion=criteria,
            single_user_id=user.pk
        )


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
    criterion: str,
    ml_input: TournesolInput,
    output: PipelineOutput,
    parameters: PipelineParameters,
):
    """
    Run Mehestan for the given criterion, in the given poll.
    """
    logger.info(
        "Mehestan computing scores for crit '%s'",
        criterion,
    )
    indiv_scores = get_individual_scores(ml_input, criteria=criterion, parameters=parameters)

    logger.info("Individual scores computed for crit '%s'", criterion)
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

    indiv_scores["criteria"] = criterion
    output.save_individual_scalings(scalings, criterion=criterion)

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
        global_scores = aggregate_scores(scaled_scores_with_voting_rights, W=parameters.W)
        global_scores["criteria"] = criterion

        # Apply squashing
        squash_function = get_squash_function(parameters)
        global_scores["uncertainty"] = 0.5 * (
            squash_function(global_scores["score"] + global_scores["uncertainty"])
            - squash_function(global_scores["score"] - global_scores["uncertainty"])
        )
        global_scores["score"] = squash_function(global_scores["score"])

        logger.info(
            "Mehestan: scores computed for crit '%s' and mode '%s'",
            criterion,
            mode,
        )
        output.save_entity_scores(global_scores, criterion=criterion, score_mode=mode.as_str())

    squash_function = get_squash_function(parameters)
    scaled_scores = scaled_scores_with_voting_rights_per_score_mode[ScoreMode.DEFAULT]
    scaled_scores["uncertainty"] = 0.5 * (
        squash_function(scaled_scores["score"] + scaled_scores["uncertainty"])
        - squash_function(scaled_scores["score"] - scaled_scores["uncertainty"])
    )
    scaled_scores["score"] = squash_function(scaled_scores["score"])
    scaled_scores["criteria"] = criterion

    output.save_individual_scores(scaled_scores, criterion=criterion)

    logger.info(
        "Mehestan: done with crit '%s'",
        criterion,
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

    criteria = poll.criterias_list

    os.register_at_fork(before=db.connections.close_all)

    criteria_to_run = [poll.main_criteria]
    if not main_criterion_only:
        criteria_to_run.extend(c for c in criteria if c != poll.main_criteria)

    # compute each criterion in parallel
    cpu_count = os.cpu_count() or 1
    cpu_count -= settings.MEHESTAN_KEEP_N_FREE_CPU

    output = TournesolPollOutput(poll_name=poll.name)

    with Pool(processes=max(1, cpu_count)) as pool:
        for _ in pool.imap_unordered(
            partial(
                run_mehestan_for_criterion,
                ml_input=ml_input,
                output=output,
                parameters=parameters
            ),
            criteria_to_run,
        ):
            pass

    save_tournesol_scores(poll)
    logger.info("Mehestan for poll '%s': Done", poll.name)
