import logging
import os
from functools import partial
from multiprocessing import Pool
from typing import Tuple

import numpy as np
import pandas as pd
from django import db

from core.models import User
from ml.inputs import MlInput, MlInputFromDb
from ml.outputs import (
    insert_or_update_contributor_score,
    save_entity_scores,
    save_tournesol_score_as_sum_of_criteria,
)
from tournesol.models import Entity, Poll
from tournesol.models.entity_score import ScoreMode

from .global_scores import get_global_scores

logger = logging.getLogger(__name__)

R_MAX = 10  # Maximum score for a comparison in the input
ALPHA = 0.01  # Signal-to-noise hyperparameter


def get_new_scores_from_online_update(
    all_comparison_user: pd.DataFrame,
    id_entity_a: str,
    id_entity_b: str,
    previous_individual_raw_scores: pd.DataFrame,
) -> Tuple[float]:
    scores = all_comparison_user[["entity_a", "entity_b", "score"]]
    if (id_entity_a, id_entity_b) not in {
        twotuple_entity_id
        for (twotuple_entity_id, _) in scores.groupby(["entity_a", "entity_b"])
    } and (id_entity_b, id_entity_a) not in {
        twotuple_entity_id
        for (twotuple_entity_id, _) in scores.groupby(["entity_a", "entity_b"])
    }:
        logger.error(
            "get_new_scores_from_online_update : no comparison found for '%s' with '%s'",
            id_entity_a,
            id_entity_b,
        )
    scores_sym = pd.concat(
        [
            scores,
            pd.DataFrame(
                {
                    "entity_a": scores.entity_b,
                    "entity_b": scores.entity_a,
                    "score": -1 * scores.score,
                }
            ),
        ]
    )

    # "Comparison tensor": matrix with all comparisons, values in [-R_MAX, R_MAX]
    r = scores_sym.pivot(index="entity_a", columns="entity_b", values="score")

    r_tilde = r / (1.0 + R_MAX)
    r_tilde2 = r_tilde**2

    # r.loc[a:b] is negative when a is prefered to b.
    l = -1.0 * r_tilde / np.sqrt(1.0 - r_tilde2)  # noqa: E741
    k = (1.0 - r_tilde2) ** 3

    L = k.mul(l).sum(axis=1)

    Kaa_np = np.array(k.sum(axis=1) + ALPHA)

    L_tilde = L / Kaa_np
    L_tilde_a = L_tilde[id_entity_a]
    L_tilde_b = L_tilde[id_entity_b]

    U_ab = -k / Kaa_np[:, None]
    U_ab = U_ab.fillna(0)

    if not previous_individual_raw_scores.index.isin([id_entity_a]).any():
        previous_individual_raw_scores.loc[id_entity_a] = 0.0

    if not previous_individual_raw_scores.index.isin([id_entity_b]).any():
        previous_individual_raw_scores.loc[id_entity_b] = 0.0

    dot_product = U_ab.dot(previous_individual_raw_scores)
    theta_star_a = L_tilde_a - dot_product[dot_product.index == id_entity_a].values
    theta_star_b = L_tilde_b - dot_product[dot_product.index == id_entity_b].values

    previous_individual_raw_scores.loc[id_entity_a] = theta_star_a
    previous_individual_raw_scores.loc[id_entity_b] = theta_star_b

    # Compute uncertainties
    scores_series = previous_individual_raw_scores.squeeze()
    scores_np = scores_series.to_numpy()
    theta_star_ab = pd.DataFrame(
        np.subtract.outer(scores_np, scores_np),
        index=scores_series.index,
        columns=scores_series.index,
    )
    K_diag = pd.DataFrame(
        data=np.diag(k.sum(axis=1) + ALPHA),
        index=k.index,
        columns=k.index,
    )
    sigma2 = (1.0 + (np.nansum(k * (l - theta_star_ab) ** 2) / 2)) / len(scores)

    delta_star = pd.Series(
        np.sqrt(sigma2) / np.sqrt(np.diag(K_diag)), index=K_diag.index
    )
    delta_star_a = delta_star[id_entity_a]
    delta_star_b = delta_star[id_entity_b]

    return (theta_star_a, delta_star_a, theta_star_b, delta_star_b)


def _run_online_heuristics_for_criterion(
    criteria: str, ml_input: MlInput, uid_a: str, uid_b: str, user_id: str, poll_pk: int
):
    poll = Poll.objects.get(pk=poll_pk)
    all_comparison_user = ml_input.get_comparisons(criteria=criteria, user_id=user_id)
    print("co", all_comparison_user.dtypes)
    entity_id_a = Entity.objects.get(uid=uid_a).pk
    entity_id_b = Entity.objects.get(uid=uid_b).pk
    if all_comparison_user.empty:
        logger.warning(
            "_run_online_heuristics_for_criterion : no comparison  for criteria '%s'",
            criteria,
        )
        return
    if (
        all_comparison_user[
            (all_comparison_user.entity_a == entity_id_a)
            & (all_comparison_user.entity_b == entity_id_b)
        ].empty
        and all_comparison_user[
            (all_comparison_user.entity_a == entity_id_b)
            & (all_comparison_user.entity_b == entity_id_a)
        ].empty
    ):
        logger.warning(
            "_run_online_heuristics_for_criterion :  \
            no comparison found for '%s' with '%s' and criteria '%s'",
            entity_id_a,
            entity_id_b,
            criteria,
        )
        return
    previous_individual_raw_scores = ml_input.get_indiv_score(
        user_id=user_id, criteria=criteria
    )
    previous_individual_raw_scores = previous_individual_raw_scores[
        ["entity_id", "score"]
    ]
    previous_individual_raw_scores = previous_individual_raw_scores.set_index(
        "entity_id"
    )
    (
        theta_star_a,
        delta_star_a,
        theta_star_b,
        delta_star_b,
    ) = get_new_scores_from_online_update(
        all_comparison_user, entity_id_a, entity_id_b, previous_individual_raw_scores
    )

    insert_or_update_contributor_score(
        poll=poll,
        entity_id=entity_id_a,
        user_id=user_id,
        score=theta_star_a,
        criteria=criteria,
        uncertainty=delta_star_a,
    )
    insert_or_update_contributor_score(
        poll=poll,
        entity_id=entity_id_b,
        user_id=user_id,
        score=theta_star_b,
        criteria=criteria,
        uncertainty=delta_star_b,
    )

    all_user_scalings = ml_input.get_all_scaling_factors(criteria=criteria)
    all_indiv_score_a = ml_input.get_indiv_score(
        entity_id=entity_id_a, criteria=criteria
    )
    if all_indiv_score_a.empty:
        logger.warning(
            "_run_online_heuristics_for_criterion :  \
            no individual score found for '%s' and criteria '%s'",
            entity_id_a,
            criteria,
        )
        return
    all_indiv_score_b = ml_input.get_indiv_score(
        entity_id=entity_id_b, criteria=criteria
    )
    if all_indiv_score_b.empty:
        logger.warning(
            "_run_online_heuristics_for_criterion :  \
            no individual score found for '%s' and criteria '%s'",
            entity_id_b,
            criteria,
        )
        return
    all_indiv_score = pd.concat([all_indiv_score_a, all_indiv_score_b])

    df = all_indiv_score.merge(
        ml_input.get_ratings_properties(), how="inner", on=["user_id", "entity_id"]
    )
    df["is_public"].fillna(False, inplace=True)
    df["is_trusted"].fillna(False, inplace=True)
    df["is_supertrusted"].fillna(False, inplace=True)

    df = df.merge(all_user_scalings, how="left", on="user_id")
    df["s"].fillna(1, inplace=True)
    df["tau"].fillna(0, inplace=True)
    df["delta_s"].fillna(0, inplace=True)
    df["delta_tau"].fillna(0, inplace=True)
    df["uncertainty"] = (
        df["s"] * df["uncertainty"]
        + df["delta_s"] * df["score"].abs()
        + df["delta_tau"]
    )
    df["score"] = df["score"] * df["s"] + df["tau"]
    df.drop(["s", "tau", "delta_s", "delta_tau"], axis=1, inplace=True)
    partial_scaled_scores_for_ab = df

    for mode in ScoreMode:
        global_scores = get_global_scores(partial_scaled_scores_for_ab, score_mode=mode)
        global_scores["criteria"] = criteria
        save_entity_scores(
            poll, global_scores, single_criteria=criteria, score_mode=mode
        )


def run_online_heuristics(
    ml_input: MlInput,
    uid_a: str,
    uid_b: str,
    user_id: str,
    poll: Poll,
    parallel_computing: bool = True,
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

    partial_online_heuristics = partial(
        _run_online_heuristics_for_criterion,
        ml_input=ml_input,
        poll_pk=poll_pk,
        uid_a=uid_a,
        uid_b=uid_b,
        user_id=user_id,
    )
    if parallel_computing:
        os.register_at_fork(before=db.connections.close_all)

        # compute each criterion in parallel
        with Pool(processes=max(1, os.cpu_count() - 1)) as pool:
            for _ in pool.imap_unordered(
                partial_online_heuristics,
                criteria,
            ):
                pass
    else:
        for criterion in criteria:
            logger.info(
                "Sequential Online Heuristic Mehestan  \
                for poll '%s  for criterion '%s': Start ",
                poll.name,
                criterion,
            )

            partial_online_heuristics(criterion)

    save_tournesol_score_as_sum_of_criteria(poll)
    logger.info("Online Heuristic Mehestan for poll '%s': Done", poll.name)


def update_user_scores(poll: Poll, user: User, uid_a: str, uid_b: str):
    ml_input = MlInputFromDb(poll_name=poll.name)
    run_online_heuristics(
        ml_input=ml_input,
        uid_a=uid_a,
        uid_b=uid_b,
        user_id=user.pk,
        poll=poll,
        parallel_computing=False,
    )
