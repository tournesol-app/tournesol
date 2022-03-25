import pandas as pd
from django.db import transaction

from core.models import User
from tournesol.models import (
    ContributorRating,
    ContributorRatingCriteriaScore,
    Entity,
    EntityCriteriaScore,
)


def save_entity_scores(poll, entity_scores, single_criteria=None):
    if isinstance(entity_scores, pd.DataFrame):
        scores_iterator = entity_scores[
            ["entity_id", "criteria", "score", "uncertainty"]
        ].itertuples(index=False)
    else:
        scores_iterator = entity_scores

    with transaction.atomic():
        scores_to_delete = EntityCriteriaScore.objects.filter(poll=poll)
        if single_criteria:
            scores_to_delete = scores_to_delete.filter(criteria=single_criteria)
        scores_to_delete.delete()

        EntityCriteriaScore.objects.bulk_create(
            EntityCriteriaScore(
                poll=poll,
                entity_id=entity_id,
                criteria=criteria,
                score=score,
                uncertainty=uncertainty,
            )
            for entity_id, criteria, score, uncertainty in scores_iterator
        )


def save_tournesol_score_as_sum_of_criteria(poll):
    entities = []
    for entity in (
        Entity.objects.filter(criteria_scores__poll=poll)
        .distinct()
        .prefetch_related("criteria_scores")
    ):
        entity.tournesol_score = 10 * sum(
            criterion.score for criterion in entity.criteria_scores.all()
        )
        entities.append(entity)
    Entity.objects.bulk_update(entities, ["tournesol_score"])


def save_contributor_scores(
    poll, contributor_scores, trusted_filter=None, single_criteria=None
):
    if isinstance(contributor_scores, pd.DataFrame):
        scores_list = list(
            contributor_scores[
                ["user_id", "entity_id", "criteria", "score", "uncertainty"]
            ].itertuples(index=False)
        )
    else:
        scores_list = list(contributor_scores)

    rating_ids = {
        (contributor_id, video_id): rating_id
        for rating_id, contributor_id, video_id in ContributorRating.objects.filter(
            poll=poll
        ).values_list("id", "user_id", "entity_id")
    }
    ratings_to_create = set(
        (contributor_id, video_id)
        for contributor_id, video_id, _, _, _ in scores_list
        if (contributor_id, video_id) not in rating_ids
    )
    created_ratings = ContributorRating.objects.bulk_create(
        ContributorRating(
            poll_id=poll.pk,
            entity_id=video_id,
            user_id=contributor_id,
        )
        for contributor_id, video_id in ratings_to_create
    )
    rating_ids.update(
        {(rating.user_id, rating.entity_id): rating.id for rating in created_ratings}
    )

    scores_to_delete = ContributorRatingCriteriaScore.objects.filter(
        contributor_rating__poll=poll
    )
    if trusted_filter is not None:
        if trusted_filter is True:
            scores_to_delete = scores_to_delete.filter(
                contributor_rating__user__in=User.trusted_users()
            )
        elif trusted_filter is False:
            scores_to_delete = scores_to_delete.exclude(
                contributor_rating__user__in=User.trusted_users()
            )
    if single_criteria is not None:
        scores_to_delete = scores_to_delete.filter(criteria=single_criteria)

    with transaction.atomic():
        scores_to_delete.delete()
        ContributorRatingCriteriaScore.objects.bulk_create(
            ContributorRatingCriteriaScore(
                contributor_rating_id=rating_ids[(contributor_id, video_id)],
                criteria=criteria,
                score=score,
                uncertainty=uncertainty,
            )
            for contributor_id, video_id, criteria, score, uncertainty in scores_list
        )
