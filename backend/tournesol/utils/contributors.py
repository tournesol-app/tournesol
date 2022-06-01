"""
Shortcut functions related to the contributors.
"""

from django.db.models.query import RawQuerySet
from django.utils import timezone

from tournesol.models.comparisons import Comparison


def get_top_public_contributors_last_month(
    poll_name: str, top: int = 10
) -> RawQuerySet:
    """
    Return the `username` of the top contributors of the last month.

    See: `get_top_public_contributors`.
    """
    now = timezone.now()

    last_month = now.month - 1
    year = now.year

    if last_month == 12:
        year -= 1

    return get_top_public_contributors(poll_name, year, last_month, top)


def get_top_public_contributors(
    poll_name: str, year: int, month: int, top: int
) -> RawQuerySet:
    """
    Return the `username` of the top contributors of a given month/year with
    their number of comparisons, ordered by this number of comparisons.

    Keyword arguments:

    poll_name -- the name of the desired poll
    year -- consider only comparisons added this year
    month -- consider only comparison added this month (january is 1, december is 12)
    top -- the maximum number of contributors to return

    Ex:

        get_top_public_contributors('videos', 2022, 2, 20)

        Return the top 20 contributors of February 2022 for the poll 'videos'.
    """

    return Comparison.objects.raw(
        f"""
        WITH public_comparisons AS (
            SELECT
                core_user.username,
                core_user.id AS user_id,
                tournesol_comparison.id AS comparison_id

            FROM tournesol_comparison

            -- this JOIN allows to filter on the desired poll
            JOIN tournesol_poll
              ON tournesol_poll.id = tournesol_comparison.poll_id

            JOIN core_user
              ON core_user.id = tournesol_comparison.user_id

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

            WHERE tournesol_poll.name = '{poll_name}'

              -- keep only comparisons from the last month
              AND EXTRACT('month' from tournesol_comparison.datetime_add)
                = {month}
              AND EXTRACT('year' from tournesol_comparison.datetime_add)
                = {year}

              -- keep only public ratings
              AND rating_1.is_public = true
              AND rating_2.is_public = true
        )
        SELECT
            user_id AS id,
            username,
            count(comparison_id) as n_comparisons

        FROM public_comparisons
        GROUP BY user_id, username
        ORDER BY n_comparisons DESC
        LIMIT {top};
    """
    )
