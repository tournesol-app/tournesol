from typing import Optional

import numpy as np
from django.conf import settings
from django.db.models import Prefetch

from core.utils.time import time_ago
from tournesol.models import ContributorRating, Entity, EntityPollRating, Poll, RateLater
from tournesol.models.rate_later import RATE_LATER_AUTO_REMOVE_DEFAULT
from tournesol.serializers.suggestion import EntityFromPollRating, EntityFromRateLater

from .base import ContributionSuggestionStrategy


class ClassicEntitySuggestionStrategy(ContributionSuggestionStrategy):
    """
    A contribution strategy that will suggest a random entity to compare.

    The entity is retrieved from the following pools:
        - user's rate-later list
        - last month recommendations
        - all time recommendations

    Expected future updates:
        - use the user's preferred language(s)
    """

    top_recommendations_limit = 400
    recent_recommendations_days = 30

    def __init__(self, request, poll: Poll):
        super().__init__(request, poll)

        rng = np.random.default_rng()
        self.selected_pool = rng.random()

    def _get_from_pool_rate_later(self) -> Optional[RateLater]:
        """
        Return a random element from the user's rate-later list.
        """
        poll = self.poll
        rate_later_size = RateLater.objects.filter(poll=poll, user=self.request.user).count()

        if not rate_later_size:
            return None

        return RateLater.objects.filter(poll=poll, user=self.request.user).prefetch_related(
            self.get_prefetch_entity_config()
        )[np.random.randint(0, rate_later_size)]

    def _get_from_pool_reco_last_month(self) -> Optional[EntityPollRating]:
        """
        Return a random element from the recent recommendations.

        Only elements that have been compared less than the setting
        `rate_later__auto_remove` are returned.
        """
        poll = self.poll
        user = self.request.user

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )

        entity_filters = {
            f"entity__{poll.entity_cls.get_filter_date_field()}__gte": time_ago(
                days=self.recent_recommendations_days
            ).isoformat()
        }

        recommendations = (
            EntityPollRating.objects.filter(
                poll=poll,
                sum_trust_scores__gte=settings.RECOMMENDATIONS_MIN_TRUST_SCORES,
                tournesol_score__gt=settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE,
            )
            .select_related("entity")
            .filter(**entity_filters)
        )

        already_compared = (
            ContributorRating.objects.filter(poll=poll, user=user)
            .select_related("entity")
            .filter(**entity_filters)
            .annotate_n_comparisons()
            .filter(n_comparisons__lt=max_threshold)
            .values_list("entity_id", flat=True)
        )

        suggestions = [reco for reco in recommendations if reco.entity_id in already_compared]

        count = len(suggestions)
        if count:
            return suggestions[np.random.randint(0, count)]

        return None

    def _get_from_pool_reco_all_time(self) -> Optional[EntityPollRating]:
        """
        Return a random element from the top recommendations.

        Only elements that have been compared less than the setting
        `rate_later__auto_remove` are returned.
        """
        poll = self.poll
        user = self.request.user

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )

        recommendations = (
            EntityPollRating.objects.filter(
                poll=poll,
                sum_trust_scores__gte=settings.RECOMMENDATIONS_MIN_TRUST_SCORES,
                tournesol_score__gt=settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE,
            ).select_related("entity")
        )[: self.top_recommendations_limit]

        already_compared = (
            ContributorRating.objects.filter(poll=poll, user=user)
            .annotate_n_comparisons()
            .filter(n_comparisons__lt=max_threshold)
            .values_list("entity_id", flat=True)
        )

        suggestions = [reco for reco in recommendations if reco.entity_id in already_compared]

        count = len(suggestions)
        if count:
            return suggestions[np.random.randint(0, count)]

        return None

    def get_prefetch_entity_config(self):
        poll = self.poll
        return Prefetch(
            "entity",
            queryset=(Entity.objects.with_prefetched_poll_ratings(poll_name=poll.name)),
        )

    def get_serializer_class(self):
        if self.selected_pool < 0.78:
            return EntityFromRateLater
        return EntityFromPollRating

    def get_result(self):
        return self.get_result_intermediate_user()

    def get_result_new_user(self):
        raise NotImplementedError

    def get_result_intermediate_user(self):
        # 0.78 ensures that more than 3/4 and less than 4/5 suggested entities
        # come from user's rate-later list.
        if self.selected_pool < 0.78:
            result = self._get_from_pool_rate_later()
            if result:
                return result

        # The remaining 22 % are divided equally between recent entities and
        # all entities. Note that "all entities" can include recent entities
        # if they are part of the top recommendations. Thus, recent entities
        # have slightly higher chance to be suggested.
        if self.selected_pool < 0.89:
            result = self._get_from_pool_reco_last_month()
            if result:
                return result

        result = self._get_from_pool_reco_all_time()
        if result:
            return result

        return None

    def get_result_advanced_user(self):
        raise NotImplementedError
