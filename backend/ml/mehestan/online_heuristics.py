import logging
from functools import partial
from typing import Set, Tuple

import numpy as np
import pandas as pd

from core.models import User
from ml.inputs import MlInput, MlInputFromDb
from ml.outputs import save_contributor_scores, save_entity_scores, save_tournesol_scores
from tournesol.models import Entity, Poll
from tournesol.models.entity_score import ScoreMode
from tournesol.utils.constants import COMPARISON_MAX

from .global_scores import get_global_scores
from .individual import calculate_lkL_from_scores
from .poll_scaling import (
    apply_poll_scaling_on_global_scores,
    apply_poll_scaling_on_individual_scaled_scores,
)

logger = logging.getLogger(__name__)

R_MAX = COMPARISON_MAX
TAU_SUBITERATION_NUMBER = 2
ALPHA = 0.01  # Signal-to-noise hyperparameter


def get_new_scores_from_online_update(
    all_comparison_user_for_criteria: pd.DataFrame,
    set_of_entity_to_update: Set[str],
    previous_individual_raw_scores: pd.DataFrame,
) -> Tuple[pd.DataFrame]:
    new_raw_scores = previous_individual_raw_scores
    new_raw_uncertainties = pd.DataFrame(set_of_entity_to_update, columns=["entity_id"])
    new_raw_uncertainties["raw_uncertainty"] = 0.0
    new_raw_uncertainties = new_raw_uncertainties.set_index("entity_id")

    scores = all_comparison_user_for_criteria[["entity_a", "entity_b", "score"]]
    all_entities = set(scores["entity_a"]) | set(scores["entity_b"])
    all_scores_values = set(scores["score"])
    # Null Matrix case
    if len(all_scores_values) == 1 and np.isnan(all_scores_values.pop()):
        new_raw_scores["raw_score"] = 0.0
        new_raw_uncertainties["raw_uncertainty"] = 0.0
        return new_raw_scores, new_raw_uncertainties

    l, k, L = calculate_lkL_from_scores(scores, filter=list(set_of_entity_to_update))
    Kaa_np = np.array(k.sum(axis=1) + ALPHA)

    # to compute dot_product, we need vector of previous_scores to be complete
    for entity in all_entities:
        if not new_raw_scores.index.isin([entity]).any():
            new_raw_scores.loc[entity] = 0.0
    new_raw_scores = new_raw_scores[new_raw_scores.index.isin(all_entities)].copy()
    new_raw_scores = (
        (L + (k.fillna(0).dot(new_raw_scores))["raw_score"]) / Kaa_np
    ).to_frame(name="raw_score")

    new_raw_scores_to_return = previous_individual_raw_scores
    new_raw_scores_to_return.loc[list(set_of_entity_to_update)] = new_raw_scores.loc[
        list(set_of_entity_to_update)
    ]

    # Compute uncertainties
    scores_series = previous_individual_raw_scores.squeeze()
    scores_np = scores_series.to_numpy()
    theta_star_ab = pd.DataFrame(
        np.subtract.outer(scores_np, scores_np),
        index=scores_series.index,
        columns=scores_series.index,
    )

    sigma2 = (1.0 + (np.nansum(k * (l - theta_star_ab) ** 2) / 2)) / len(scores)

    delta_star = pd.Series(np.sqrt(sigma2) / np.sqrt(Kaa_np), index=k.index)
    new_raw_uncertainties = delta_star.to_frame(name="raw_uncertainty")

    return new_raw_scores_to_return, new_raw_uncertainties


def _run_online_heuristics_for_criterion(
    criteria: str,
    ml_input: MlInput,
    uid_a: str,
    uid_b: str,
    user_id: str,
    poll_pk: int,
    delete_comparison_case: bool,
):
    """
    This function apply the online heuristics for a criteria. There is 3 cases :
    1. a new comparison has been made
    2. a comparison has been updated
    3. a comparison has been deleted

    * For each case, this function need to know which entities
        are being concerned as input and what to do
    * For each case, we first check if the input are compliant
        with the data (check_requirements_are_good_for_online_heuristics)
    * For each case, then we read the previous raw scores
        (compute_and_update_individual_scores_online_heuristics) and compute new scores
    * For each case, we reapply scaling (individual) from previous scale
    * For each case, we compute new global scores for the two entities
        and we apply poll level scaling at global scores

    """
    poll = Poll.objects.get(pk=poll_pk)
    all_comparison_of_user_for_criteria = ml_input.get_comparisons(
        criteria=criteria, user_id=user_id
    )

    entity_id_a = Entity.objects.get(uid=uid_a).pk
    entity_id_b = Entity.objects.get(uid=uid_b).pk

    # For delete comparison, we reintroduce the comparison with a 0 score and treat like an update
    if delete_comparison_case:
        df_new_row = pd.DataFrame(
            [(user_id, entity_id_a, entity_id_b, criteria, np.NaN, 0)],
            columns=["user_id", "entity_a", "entity_b", "criteria", "score", "weight"],
        )
        all_comparison_of_user_for_criteria = pd.concat(
            [all_comparison_of_user_for_criteria, df_new_row]
        )

    if not check_requirements_are_good_for_online_heuristics(
        criteria,
        all_comparison_of_user_for_criteria,
        entity_id_a,
        entity_id_b,
    ):
        return

    set_of_entity_to_update = {entity_id_a, entity_id_b}
    previous_individual_raw_scores = ml_input.get_indiv_score(
        user_id=user_id, criteria=criteria
    )
    previous_individual_raw_scores = previous_individual_raw_scores[
        ["entity_id", "raw_score"]
    ]
    previous_individual_raw_scores = previous_individual_raw_scores.set_index(
        "entity_id"
    )
    new_raw_scores = previous_individual_raw_scores
    for tau in range(0, TAU_SUBITERATION_NUMBER):
        if tau > 0:
            set_of_entity_to_update = compute_and_give_next_set_of_entity_to_update(
                set_of_entity_to_update, all_comparison_of_user_for_criteria
            )

        # Now with previous trick and valid condition check,
        # all_comparison_of_user_for_criteria have a pair (entity_id_b,entity_id_a)
        new_raw_scores, new_raw_uncertainties = get_new_scores_from_online_update(
            all_comparison_of_user_for_criteria,
            set_of_entity_to_update,
            new_raw_scores,
        )

    # so far we have recompute new indiv score for a and b and neighbours,
    # we need to recompute global score for a and b
    # in order to so, we need all individual scaled score concerning a and b
    # we will get those and inject the new raw score before scaling for {a|b}/criteria/user_id
    theta_star_a = new_raw_scores.loc[
        new_raw_scores.index == entity_id_a, "raw_score"
    ].values.squeeze()[()]
    delta_star_a = new_raw_uncertainties.loc[
        new_raw_uncertainties.index == entity_id_a, "raw_uncertainty"
    ].values.squeeze()[()]
    theta_star_b = new_raw_scores.loc[
        new_raw_scores.index == entity_id_b, "raw_score"
    ].values.squeeze()[()]
    delta_star_b = new_raw_uncertainties.loc[
        new_raw_uncertainties.index == entity_id_b, "raw_uncertainty"
    ].values.squeeze()[()]
    new_data_a = (entity_id_a, theta_star_a, delta_star_a)
    new_data_b = (entity_id_b, theta_star_b, delta_star_b)

    new_df = new_raw_scores.join(new_raw_uncertainties)
    partial_scaled_scores_for_ab = (
        apply_and_return_scaling_on_individual_scores_online_heuristics(
            criteria, ml_input, new_data_a, new_data_b, user_id
        )
    )

    if not partial_scaled_scores_for_ab.empty:
        calculate_and_save_global_scores_in_all_score_mode(
            criteria, poll, partial_scaled_scores_for_ab
        )
        apply_poll_scaling_on_individual_scaled_scores(
            poll, partial_scaled_scores_for_ab
        )

        # we want to save only individual scores of user
        score_to_save = ml_input.get_indiv_score(user_id=user_id)

        for entity_id_a, (theta_star_a, delta_star_a) in new_df.iterrows():
            score_to_save = add_or_update_df_indiv_score(
                user_id, entity_id_a, theta_star_a, delta_star_a, score_to_save
            )

        score_to_save["criteria"] = criteria

        save_contributor_scores(
            poll,
            score_to_save,
            single_criteria=criteria,
            single_user_id=user_id,
        )


def compute_and_give_next_set_of_entity_to_update(
    set_of_entity_to_update: Set[str], all_comparison_of_user_for_criteria: pd.DataFrame
):
    set_of_neighbours_1 = set(
        all_comparison_of_user_for_criteria.loc[
            all_comparison_of_user_for_criteria.entity_a.isin(set_of_entity_to_update)
        ]["entity_b"]
    )
    set_of_neighbours_2 = set(
        all_comparison_of_user_for_criteria.loc[
            all_comparison_of_user_for_criteria.entity_b.isin(set_of_entity_to_update)
        ]["entity_a"]
    )
    return set_of_neighbours_1 | set_of_neighbours_2 | set_of_entity_to_update


def calculate_and_save_global_scores_in_all_score_mode(
    criteria: str,
    poll: Poll,
    df_partial_scaled_scores_for_ab: pd.DataFrame,
):
    for mode in ScoreMode:
        global_scores = get_global_scores(
            df_partial_scaled_scores_for_ab, score_mode=mode
        )
        global_scores["criteria"] = criteria

        apply_poll_scaling_on_global_scores(poll, global_scores)

        save_entity_scores(
            poll,
            global_scores,
            single_criteria=criteria,
            score_mode=mode,
            delete_all=False,
        )


def apply_and_return_scaling_on_individual_scores_online_heuristics(
    criteria: str, ml_input: MlInput, new_data_a: Tuple, new_data_b: Tuple, user_id: int
) -> pd.DataFrame:
    """
    return df with all individual scaled scores concerning entity A and B,
    in order to recompute global score of A and B
    """
    entity_id_a, theta_star_a, delta_star_a = new_data_a
    entity_id_b, theta_star_b, delta_star_b = new_data_b
    all_user_scalings = ml_input.get_user_scalings()

    all_indiv_score = ml_input.get_indiv_score(
        entity_id_in=[entity_id_a, entity_id_b], criteria=criteria
    )

    if all_indiv_score.empty:
        all_indiv_score = pd.DataFrame(
            {
                "user_id": pd.Series(dtype="int64"),
                "entity_id": pd.Series(dtype="int64"),
                "raw_score": pd.Series(dtype="float64"),
                "raw_uncertainty": pd.Series(dtype="float64"),
            }
        )

    all_indiv_score = add_or_update_df_indiv_score(
        user_id, entity_id_a, theta_star_a, delta_star_a, all_indiv_score
    )
    all_indiv_score = add_or_update_df_indiv_score(
        user_id, entity_id_b, theta_star_b, delta_star_b, all_indiv_score
    )

    df_ratings = ml_input.get_ratings_properties(django_orm_union=False)
    df = all_indiv_score.merge(df_ratings, how="inner", on=["user_id", "entity_id"])

    df["is_public"].fillna(False, inplace=True)
    df["is_trusted"].fillna(False, inplace=True)
    df["is_supertrusted"].fillna(False, inplace=True)

    df = df.merge(all_user_scalings, how="left", on="user_id")
    df["scale"].fillna(1, inplace=True)
    df["translation"].fillna(0, inplace=True)
    df["scale_uncertainty"].fillna(0, inplace=True)
    df["translation_uncertainty"].fillna(0, inplace=True)

    df["uncertainty"] = (
        df["scale"] * df["raw_uncertainty"]
        + df["scale_uncertainty"] * df["raw_score"].abs()
        + df["translation_uncertainty"]
    )
    df["score"] = df["raw_score"] * df["scale"] + df["translation"]

    df.drop(
        ["scale", "translation", "scale_uncertainty", "translation_uncertainty"],
        axis=1,
        inplace=True,
    )
    return df


def add_or_update_df_indiv_score(
    user_id, entity_id_a, theta_star_a, delta_star_a, all_indiv_score
):
    if all_indiv_score.empty:
        all_indiv_score = pd.DataFrame(
            {
                "user_id": pd.Series(dtype="int64"),
                "entity_id": pd.Series(dtype="int64"),
                "raw_score": pd.Series(dtype="float64"),
                "raw_uncertainty": pd.Series(dtype="float64"),
            }
        )
    if all_indiv_score[
        (all_indiv_score["entity_id"] == entity_id_a)
        & (all_indiv_score["user_id"] == user_id)
    ].empty:
        df_new_row = pd.DataFrame(
            [(user_id, entity_id_a, theta_star_a, delta_star_a)],
            columns=["user_id", "entity_id", "raw_score", "raw_uncertainty"],
        )
        all_indiv_score = pd.concat([all_indiv_score, df_new_row])
    else:
        all_indiv_score.loc[
            (all_indiv_score["entity_id"] == entity_id_a)
            & (all_indiv_score["user_id"] == user_id),
            ["raw_score", "raw_uncertainty"],
        ] = (theta_star_a, delta_star_a)

    return all_indiv_score


def check_requirements_are_good_for_online_heuristics(
    criteria: str,
    df_all_comparison_of_user_for_criteria: pd.DataFrame,
    entity_id_a: int,
    entity_id_b: int,
):
    if df_all_comparison_of_user_for_criteria.empty:
        logger.warning(
            "_run_online_heuristics_for_criterion : no comparison  for criteria '%s'",
            criteria,
        )
        return False
    if (
        df_all_comparison_of_user_for_criteria[
            (df_all_comparison_of_user_for_criteria.entity_a == entity_id_a)
            & (df_all_comparison_of_user_for_criteria.entity_b == entity_id_b)
        ].empty
        and df_all_comparison_of_user_for_criteria[
            (df_all_comparison_of_user_for_criteria.entity_a == entity_id_b)
            & (df_all_comparison_of_user_for_criteria.entity_b == entity_id_a)
        ].empty
    ):
        logger.warning(
            "_run_online_heuristics_for_criterion :  \
            no comparison found for '%s' with '%s' and criteria '%s'",
            entity_id_a,
            entity_id_b,
            criteria,
        )
        return False
    return True


def run_online_heuristics(
    ml_input: MlInput,
    uid_a: str,
    uid_b: str,
    user_id: str,
    poll: Poll,
    delete_comparison_case: bool,
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
    logger.info("Online Heuristic Mehestan for poll '%s': Start", poll.name)

    # Avoid passing model's instances as arguments to the function run by the
    # child processes. See this method docstring.
    poll_pk = poll.pk
    criteria = poll.criterias_list

    _run_online_heuristics_for_criterion(
        ml_input=ml_input,
        poll_pk=poll_pk,
        criteria=poll.main_criteria,
        uid_a=uid_a,
        uid_b=uid_b,
        user_id=user_id,
        delete_comparison_case=delete_comparison_case,
    )

    save_tournesol_scores(poll, list_of_entities=[uid_a, uid_b])
    logger.info(
        "Online Heuristic Mehestan for poll '%s': main_criteria Done", poll.name
    )

    partial_online_heuristics = partial(
        _run_online_heuristics_for_criterion,
        ml_input=ml_input,
        poll_pk=poll_pk,
        uid_a=uid_a,
        uid_b=uid_b,
        user_id=user_id,
        delete_comparison_case=delete_comparison_case,
    )
    # compute each criterion in parallel
    remaining_criteria = [c for c in criteria if c != poll.main_criteria]

    for criterion in remaining_criteria:
        logger.info(
            "Sequential Online Heuristic Mehestan  \
            for poll '%s  for criterion '%s': Start ",
            poll.name,
            criterion,
        )
        partial_online_heuristics(criterion)

    logger.info("Online Heuristic Mehestan for poll '%s': Done", poll.name)


def update_user_scores(
    poll: Poll, user: User, uid_a: str, uid_b: str, delete_comparison_case: bool
):
    ml_input = MlInputFromDb(poll_name=poll.name)
    run_online_heuristics(
        ml_input=ml_input,
        uid_a=uid_a,
        uid_b=uid_b,
        user_id=user.pk,
        poll=poll,
        delete_comparison_case=delete_comparison_case,
    )
