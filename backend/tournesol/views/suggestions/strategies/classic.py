import random

from django.conf import settings

from core.utils.time import time_ago
from tournesol.models import ContributorRating, EntityPollRating, RateLater
from tournesol.models.rate_later import RATE_LATER_AUTO_REMOVE_DEFAULT
from tournesol.serializers.suggestion import ResultFromPollRating

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

    n_entity_rate_later = 14
    n_entity_reco_last_month = 3
    n_entity_reco_all_time = 3

    top_recommendations_limit = 400
    recent_recommendations_days = 30

    def _get_recommendations(self, entity_filters, exclude_uids: list[int]) -> list[int]:
        poll = self.poll

        return (
            EntityPollRating.objects.filter(
                poll=poll,
                sum_trust_scores__gte=settings.RECOMMENDATIONS_MIN_TRUST_SCORES,
                tournesol_score__gt=settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE,
            )
            .select_related("entity")
            .filter(**entity_filters)
            .exclude(entity_id__in=exclude_uids)
            .values_list("entity_id", flat=True)
        )

    def _get_already_compared(self, entity_filters) -> list[int]:
        poll = self.poll
        user = self.request.user

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )

        return (
            ContributorRating.objects.filter(poll=poll, user=user)
            .select_related("entity")
            .filter(**entity_filters)
            .annotate_n_comparisons()
            .filter(n_comparisons__gte=max_threshold)
            .values_list("entity_id", flat=True)
        )

    def _uids_from_pool_rate_later(self) -> list[int]:
        """
        Return random UIDs from the user's rate-later list.
        """
        poll = self.poll
        user = self.request.user

        rate_later_size = RateLater.objects.filter(poll=poll, user=user).count()

        if not rate_later_size:
            return []

        results = RateLater.objects.filter(poll=poll, user=user).values_list(
            "entity_id", flat=True
        )

        return random.sample(list(results), min(rate_later_size, self.n_entity_rate_later))

    def _uids_from_pool_reco_last_month(self, exclude_uids: list[int]) -> list[int]:
        """
        Return random UIDs from the recent recommendations.

        Only UIDs of entities that have been compared less than the user's
        setting `rate_later__auto_remove` are returned.
        """
        poll = self.poll

        entity_filters = {
            f"entity__{poll.entity_cls.get_filter_date_field()}__gte": time_ago(
                days=self.recent_recommendations_days
            ).isoformat(),
        }

        recommendations = self._get_recommendations(entity_filters, exclude_uids)
        already_compared = self._get_already_compared(entity_filters)
        results = [reco for reco in recommendations if reco not in already_compared]

        size = len(results)
        if not size:
            return []

        return random.sample(results, min(size, self.n_entity_reco_last_month))

    def _uids_from_pool_reco_all_time(self, exclude_uids: list[int]) -> list[int]:
        """
        Return random UIDs from the top recommendations.

        Only UIDs of entities that have been compared less than the user's
        setting `rate_later__auto_remove` are returned.
        """
        poll = self.poll

        entity_filters = {
            f"entity__{poll.entity_cls.get_filter_date_field()}__lt": time_ago(
                days=self.recent_recommendations_days
            ).isoformat(),
        }

        recommendations = self._get_recommendations(entity_filters, exclude_uids)[
            : self.top_recommendations_limit
        ]
        already_compared = self._get_already_compared(entity_filters)
        results = [reco for reco in recommendations if reco not in already_compared]

        size = len(results)
        if not size:
            return []

        return random.sample(results, min(size, self.n_entity_reco_all_time))

    def get_serializer_class(self):
        return ResultFromPollRating

    def get_results(self):
        return self.get_result_for_user_intermediate()

    def get_result_for_user_new(self):
        raise NotImplementedError

    def get_result_for_user_intermediate(self):
        poll = self.poll
        rate_later = self._uids_from_pool_rate_later()
        last_month = self._uids_from_pool_reco_last_month(rate_later)
        all_time = self._uids_from_pool_reco_all_time(rate_later + last_month)

        results = (
            EntityPollRating.objects.filter(
                poll=poll,
            )
            .select_related("entity")
            .filter(entity_id__in=rate_later + last_month + all_time)
        )

        return results

    def get_result_for_user_advanced(self):
        raise NotImplementedError
