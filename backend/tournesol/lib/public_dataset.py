"""
The public dataset library.
"""
from django.db.models import QuerySet


def get_dataset(poll_name: str) -> QuerySet:
    """
    Retrieve the public dataset from the database and return a non-evaluated
    Django `RawQuerySet`.
    """
    from tournesol.models.comparisons import Comparison  # pylint: disable=import-outside-toplevel

    return Comparison.objects.raw(
        """
        SELECT
            tournesol_comparison.id,

            core_user.username,
            entity_1.uid AS uid_a,
            entity_2.uid AS uid_b,
            comparisoncriteriascore.criteria,
            comparisoncriteriascore.weight,
            comparisoncriteriascore.score

        FROM tournesol_comparison

        -- this JOIN allows to filter on the desired poll
        JOIN tournesol_poll
          ON tournesol_poll.id = tournesol_comparison.poll_id

        JOIN core_user
          ON core_user.id = tournesol_comparison.user_id

        JOIN tournesol_comparisoncriteriascore AS comparisoncriteriascore
          ON comparisoncriteriascore.comparison_id = tournesol_comparison.id

        JOIN tournesol_entity AS entity_1
          ON entity_1.id = tournesol_comparison.entity_1_id

        JOIN tournesol_entity AS entity_2
          ON entity_2.id = tournesol_comparison.entity_2_id

        -- this JOIN allows to filter by public ratings for the entity_1
        -- the poll has been already filtered, no need to filter it again
        JOIN tournesol_contributorrating AS rating_1
          ON rating_1.entity_id = tournesol_comparison.entity_1_id
         AND rating_1.user_id = tournesol_comparison.user_id

        -- this JOIN allows to filter by public ratings for the entity_2
        -- the poll has been already filtered, no need to filter it again
        JOIN tournesol_contributorrating AS rating_2
          ON rating_2.entity_id = tournesol_comparison.entity_2_id
         AND rating_2.user_id = tournesol_comparison.user_id

        WHERE tournesol_poll.name = %(poll_name)s
          -- keep only public ratings
          AND rating_1.is_public = true
          AND rating_2.is_public = true
        """,
        {"poll_name": poll_name},
    )


def get_users_dataset(poll_name: str) -> QuerySet:
    """
    Retrieve users with at least one public comparison and return a
    non-evaluated Django `RawQuerySet`.
    """
    from core.models import User  # pylint: disable=import-outside-toplevel

    return User.objects.raw(
        """
        SELECT DISTINCT
            core_user.id,
            core_user.username,
            core_user.trust_score

        FROM core_user

        -- all the conditions below are there only to limit the result
        -- to users who made public comparisons. They should be similar
        -- to the ones in `get_dataset`

        JOIN tournesol_comparison
          ON tournesol_comparison.user_id = core_user.id

        JOIN tournesol_poll
          ON tournesol_poll.id = tournesol_comparison.poll_id

        JOIN tournesol_entity AS entity_1
          ON entity_1.id = tournesol_comparison.entity_1_id

        JOIN tournesol_entity AS entity_2
          ON entity_2.id = tournesol_comparison.entity_2_id

        JOIN tournesol_contributorrating AS rating_1
          ON rating_1.entity_id = tournesol_comparison.entity_1_id
         AND rating_1.user_id = tournesol_comparison.user_id

        JOIN tournesol_contributorrating AS rating_2
          ON rating_2.entity_id = tournesol_comparison.entity_2_id
         AND rating_2.user_id = tournesol_comparison.user_id

        WHERE tournesol_poll.name = %(poll_name)s
          -- keep only public ratings
          AND rating_1.is_public = true
          AND rating_2.is_public = true

        ORDER BY core_user.username
        """,
        {"poll_name": poll_name},
    )


def get_public_contributor_rating_criteria_scores_dataset(poll_name: str) -> QuerySet:
    """
    Retrieve ContributorRatingCriteriaScores made on public comparisons and return a
    non-evaluated Django `RawQuerySet`.
    """
    from tournesol.models import (  # pylint: disable=import-outside-toplevel
        ContributorRatingCriteriaScore,
    )

    return (
        ContributorRatingCriteriaScore
        .objects
        .select_related('contributor_rating')
        .select_related('contributor_rating__poll')
        .select_related('contributor_rating__user')
        .select_related('contributor_rating__entity')
        .filter(contributor_rating__poll__name=poll_name)
        .filter(contributor_rating__is_public=True)
        .order_by(
            'contributor_rating__user__username',
            'contributor_rating__entity__uid',
            'criteria',
        )
    )
