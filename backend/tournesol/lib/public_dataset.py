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
