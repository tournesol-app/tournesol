import collections
from datetime import datetime, timedelta

from tournesol.models.comparisons import Comparison
from tournesol.models.poll import DEFAULT_POLL_NAME
from tournesol.models.ratings import ContributorRating


def get_previous_month_best_public_contributor():
    """Return the best public contributor of the previous month."""
        
    now = datetime.now()
    last_month = datetime(now.year, now.month, 1) - timedelta(days=15)
    
    public_data = (
        ContributorRating.objects
        .filter(is_public=True, poll__name=DEFAULT_POLL_NAME)
        .select_related("user", "entity")
    )
    
    public_videos = set((rating.user, rating.entity) for rating in public_data)
    
    comparisons = (
        Comparison.objects
        .filter(poll__name=DEFAULT_POLL_NAME, 
                datetime_add__month=last_month.month,
                datetime_add__year=last_month.year)
        .select_related("entity_1", "entity_2", "user")
    )
    
    public_comparisons = [
        comparison
        for comparison in comparisons
        if (
            (comparison.user, comparison.entity_1) in public_videos
            and (comparison.user, comparison.entity_2) in public_videos
        )
    ]
        
    public_usernames = [comparison.user.username for comparison in public_comparisons]
 
    best_contributor_counter = collections.Counter(public_usernames)

    return best_contributor_counter.most_common(10)
        