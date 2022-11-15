from typing import Iterable, Optional, Union

import numpy as np
import pandas as pd
from django.db import transaction

from tournesol.models import (
    ContributorRating,
    ContributorRatingCriteriaScore,
    ContributorScaling,
    Entity,
    EntityCriteriaScore,
    Poll,
)
from tournesol.models.entity_score import ScoreMode
from tournesol.models.poll import ALGORITHM_MEHESTAN

from .inputs import MlInputFromDb


def save_entity_scores(
    poll,
    entity_scores: Union[pd.DataFrame, Iterable[tuple]],
    single_criteria=None,
    score_mode=ScoreMode.DEFAULT,
):
    if isinstance(entity_scores, pd.DataFrame):
        scores_iterator = entity_scores[
            ["entity_id", "criteria", "score", "uncertainty", "deviation"]
        ].itertuples(index=False)
    else:
        scores_iterator = entity_scores

    with transaction.atomic():
        scores_to_delete = EntityCriteriaScore.objects.filter(
            poll=poll, score_mode=score_mode
        )
        if single_criteria:
            scores_to_delete = scores_to_delete.filter(criteria=single_criteria)
        scores_to_delete.delete()

        EntityCriteriaScore.objects.bulk_create(
            (
                EntityCriteriaScore(
                    poll=poll,
                    entity_id=entity_id,
                    criteria=criteria,
                    score=score,
                    uncertainty=uncertainty,
                    deviation=deviation,
                    score_mode=score_mode,
                )
                for entity_id, criteria, score, uncertainty, deviation in scores_iterator
            ),
            batch_size=10000,
        )


def save_tournesol_scores(poll):
    entities = []
    for entity in (
        Entity.objects.filter(all_criteria_scores__poll=poll)
        .distinct()
        .with_prefetched_scores(poll_name=poll.name)
    ):
        if poll.algorithm == ALGORITHM_MEHESTAN:
            # The tournesol score is simply the score associated with the main criteria
            entity.tournesol_score = next(
                (
                    s.score
                    for s in entity.criteria_scores
                    if s.criteria == poll.main_criteria
                ),
                None,
            )
        else:
            entity.tournesol_score = 10 * sum(
                criterion.score for criterion in entity.criteria_scores
            )
        entities.append(entity)
    Entity.objects.bulk_update(entities, ["tournesol_score"])


def apply_score_scalings(poll: Poll, contributor_scores: pd.DataFrame):
    """
    Apply individual and poll-level scalings based on input "raw_score", and "raw_uncertainty".

    Params:
        poll: Poll,
        contributor_scores: DataFrame with columns:
            user_id: int
            entity_id: int
            criteria: str
            raw_score: float
            raw_uncertainty: float

    Returns:
        DataFrame with additional columns "score" and "uncertainty".
    """
    if poll.algorithm != ALGORITHM_MEHESTAN:
        contributor_scores["score"] = contributor_scores["raw_score"]
        contributor_scores["uncertainty"] = contributor_scores["raw_uncertainty"]
        return contributor_scores

    ml_input = MlInputFromDb(poll_name=poll.name)
    scalings = ml_input.get_user_scalings().set_index(["user_id", "criteria"])
    contributor_scores = contributor_scores.join(
        scalings, on=["user_id", "criteria"], how="left"
    )
    contributor_scores["scale"].fillna(1, inplace=True)
    contributor_scores["translation"].fillna(0, inplace=True)
    contributor_scores["scale_uncertainty"].fillna(0, inplace=True)
    contributor_scores["translation_uncertainty"].fillna(0, inplace=True)

    # Apply individual scaling
    contributor_scores["uncertainty"] = (
        contributor_scores["scale"] * contributor_scores["raw_uncertainty"]
        + contributor_scores["scale_uncertainty"]
        * contributor_scores["raw_score"].abs()
        + contributor_scores["translation_uncertainty"]
    )
    contributor_scores["score"] = (
        contributor_scores["raw_score"] * contributor_scores["scale"]
        + contributor_scores["translation"]
    )

    # Apply poll scaling
    scale_function = poll.scale_function
    contributor_scores["uncertainty"] = 0.5 * (
        scale_function(contributor_scores["score"] + contributor_scores["uncertainty"])
        - scale_function(
            contributor_scores["score"] - contributor_scores["uncertainty"]
        )
    )
    contributor_scores["score"] = scale_function(contributor_scores["score"])
    return contributor_scores


def save_contributor_scores(
    poll: Poll,
    contributor_scores: Union[pd.DataFrame, Iterable[tuple]],
    single_criteria: Optional[str] = None,
    single_user_id: Optional[int] = None,
) -> None:
    if not isinstance(contributor_scores, pd.DataFrame):
        contributor_scores = pd.DataFrame(
            contributor_scores,
            columns=[
                "user_id",
                "entity_id",
                "criteria",
                "raw_score",
                "raw_uncertainty",
                "voting_right",
            ],
        )

    if "score" not in contributor_scores:
        # Scaled "score" and "uncertainty" need to be computed
        # based on raw_score and raw_uncertainty
        contributor_scores = apply_score_scalings(poll, contributor_scores)

    ratings = ContributorRating.objects.filter(poll=poll)
    if single_user_id is not None:
        ratings = ratings.filter(user_id=single_user_id)

    rating_ids = {
        (contributor_id, entity_id): rating_id
        for rating_id, contributor_id, entity_id in ratings.values_list(
            "id", "user_id", "entity_id"
        )
    }
    ratings_to_create = set(
        (contributor_id, entity_id)
        for contributor_id, entity_id in contributor_scores[
            ["user_id", "entity_id"]
        ].itertuples(index=False)
        if (contributor_id, entity_id) not in rating_ids
    )
    ContributorRating.objects.bulk_create(
        (
            ContributorRating(
                poll_id=poll.pk,
                entity_id=entity_id,
                user_id=contributor_id,
            )
            for contributor_id, entity_id in ratings_to_create
        ),
        ignore_conflicts=True,
    )
    # Refresh the `ratings_id` with the newly created `ContributorRating`s.
    rating_ids.update(
        {
            (contributor_id, entity_id): rating_id
            for rating_id, contributor_id, entity_id in ratings.values_list(
                "id", "user_id", "entity_id"
            )
        }
    )

    scores_to_delete = ContributorRatingCriteriaScore.objects.filter(
        contributor_rating__poll=poll
    )

    if single_criteria is not None:
        scores_to_delete = scores_to_delete.filter(criteria=single_criteria)

    if single_user_id is not None:
        scores_to_delete = scores_to_delete.filter(
            contributor_rating__user_id=single_user_id
        )

    with transaction.atomic():
        scores_to_delete.delete()
        ContributorRatingCriteriaScore.objects.bulk_create(
            ContributorRatingCriteriaScore(
                contributor_rating_id=rating_ids[(row.user_id, row.entity_id)],
                criteria=row.criteria,
                score=row.score,
                uncertainty=row.uncertainty,
                raw_score=row.raw_score,
                raw_uncertainty=row.raw_uncertainty,
                # row contains `voting_right` when it comes from a full ML run, but not in the case
                # of online individual updates. As online updates do not update the global scores,
                # it makes sense to set the voting right equal to 0. temporarily and to expect it
                # to be updated during the next ML run.
                voting_right=row.voting_right if hasattr(row, 'voting_right') else 0.0,
            )
            for _, row in contributor_scores.iterrows()
        )


def save_contributor_scalings(poll: Poll, criteria: str, scalings: pd.DataFrame):
    scalings_iterator = (
        scalings[["s", "delta_s", "tau", "delta_tau"]]
        .replace({np.nan: None})
        .itertuples(index=True)
    )

    with transaction.atomic():
        ContributorScaling.objects.filter(poll=poll, criteria=criteria).delete()
        ContributorScaling.objects.bulk_create(
            (
                ContributorScaling(
                    poll=poll,
                    criteria=criteria,
                    user_id=user_id,
                    scale=s,
                    scale_uncertainty=delta_s,
                    translation=tau,
                    translation_uncertainty=delta_tau,
                )
                for user_id, s, delta_s, tau, delta_tau in scalings_iterator
            ),
            batch_size=10000,
        )
