"""
Shortcuts functions related to the contributors.
"""

import collections
from datetime import timedelta
from typing import List, Tuple

from django.utils import timezone

from tournesol.models.comparisons import Comparison


def get_last_month_top_public_contributors(poll_name: str) -> List[str]:
    """
    Return the top contributors of the previous month with their number of
    comparisons, ordered by this number of comparisons.
    """

    top_contributors = Comparison.objects.raw(
        f"""
        WITH public_comparisons AS (
            SELECT
                core_user.username,
                core_user.id AS user_id,
                tournesol_comparison.id AS comparison_id
            FROM
                tournesol_comparison
    
            -- this JOIN allows to filter on the desired poll
            JOIN tournesol_poll
              ON tournesol_poll.id = tournesol_comparison.poll_id
    
            JOIN core_user
              ON core_user.id = tournesol_comparison.user_id
    
            -- this JOIN allows to filter by public entity_1 ratings
            -- the poll has been already filtered, no need to filter it again here
            JOIN tournesol_contributorrating AS rating_1
              ON rating_1.entity_id = tournesol_comparison.entity_1_id
             AND rating_1.user_id = tournesol_comparison.user_id
    
            -- this JOIN allows to filter by public entity_2 ratings
            -- the poll has been already filtered, no need to filter it again here
            JOIN tournesol_contributorrating AS rating_2
              ON rating_2.entity_id = tournesol_comparison.entity_2_id
             AND rating_2.user_id = tournesol_comparison.user_id
    
            WHERE tournesol_poll.name = '{poll_name}'
    
              AND EXTRACT('month' from tournesol_comparison.datetime_add) = EXTRACT('month' from current_timestamp) - 1
              AND EXTRACT('year' from tournesol_comparison.datetime_add) = EXTRACT('year' from current_timestamp)
    
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
            LIMIT 10;
    """
    )

    return top_contributors


def get_last_month_top_public_contributors_RAW_AND_COUNTER(
    poll_name: str,
) -> List[Tuple]:
    """
    Return the top contributors of the previous month with their number of
    comparisons, ordered by this number of comparisons.
    """

    now = timezone.now()
    last_month = timezone.datetime(
        now.year, now.month, 1, tzinfo=timezone.get_current_timezone()
    ) - timedelta(days=15)

    public_comparisons = Comparison.objects.raw(
        f"""
        SELECT
            core_user.username,
            tournesol_comparison.id
        FROM
            tournesol_comparison

        -- this JOIN allows to filter on the desired poll
        JOIN tournesol_poll
          ON tournesol_poll.id = tournesol_comparison.poll_id

        JOIN core_user
          ON core_user.id = tournesol_comparison.user_id

        -- this JOIN allows to filter by public entity_1 ratings
        -- the poll has been already filtered, no need to filter it again here
        JOIN tournesol_contributorrating AS rating_1
          ON rating_1.entity_id = tournesol_comparison.entity_1_id
         AND rating_1.user_id = tournesol_comparison.user_id

        -- this JOIN allows to filter by public entity_2 ratings
        -- the poll has been already filtered, no need to filter it again here
        JOIN tournesol_contributorrating AS rating_2
          ON rating_2.entity_id = tournesol_comparison.entity_2_id
         AND rating_2.user_id = tournesol_comparison.user_id

        WHERE tournesol_poll.name = '{poll_name}'

          AND EXTRACT('month' from tournesol_comparison.datetime_add) = EXTRACT('month' from current_timestamp) - 1
          AND EXTRACT('year' from tournesol_comparison.datetime_add) = EXTRACT('year' from current_timestamp)

          AND rating_1.is_public = true
          AND rating_2.is_public = true;
    """
    )

    usernames = [comparison.username for comparison in public_comparisons]
    top_contributors_counter = collections.Counter(usernames)
    return top_contributors_counter.most_common(10)
