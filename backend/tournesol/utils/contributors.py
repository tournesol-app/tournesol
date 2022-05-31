"""
Shortcuts functions related to the contributors.
"""

import collections
from datetime import datetime, timedelta
from typing import List, Tuple

from tournesol.models.comparisons import Comparison
from tournesol.models.ratings import ContributorRating


def get_last_month_top_public_contributors(poll_name: str) -> List[Tuple]:
    """
    Return the top contributors of the previous month with their number of
    comparisons, ordered by this number of comparisons.
    """

    now = datetime.now()
    last_month = datetime(now.year, now.month, 1) - timedelta(days=15)

    public_ratings = (
        ContributorRating.objects.filter(is_public=True, poll__name=poll_name)
        .select_related("user", "entity")
        .values_list("user__username", "entity__uid")
    )

    comparisons = (
        Comparison.objects.filter(
            poll__name=poll_name,
            datetime_add__month=last_month.month,
            datetime_add__year=last_month.year,
        )
        .select_related("entity_1", "entity_2", "user")
        .values("entity_1__uid", "entity_2__uid", "user__username")
    )

    public_comparisons = [
        comparison
        for comparison in comparisons
        if (
            (comparison["user__username"], comparison["entity_1__uid"])
            in public_ratings
            and (comparison["user__username"], comparison["entity_2__uid"])
            in public_ratings
        )
    ]

    usernames = [comparison["user__username"] for comparison in public_comparisons]

    top_contributors_counter = collections.Counter(usernames)
    return top_contributors_counter.most_common(10)
