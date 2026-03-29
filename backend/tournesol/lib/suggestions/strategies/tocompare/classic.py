import random

from core.utils.time import time_ago
from tournesol.lib.suggestions.strategies.tocompare.base import PoolBasedEntitySuggestionStrategy
from tournesol.models import ContributorRating, Entity, RateLater
from tournesol.models.rate_later import RATE_LATER_AUTO_REMOVE_DEFAULT


class ClassicEntitySuggestionStrategy(PoolBasedEntitySuggestionStrategy):
    """
    A contribution strategy that suggests random entities for comparison.

    The entity are retrieved from the following pools:
        - entities already compared by the users (but not enough)
        - entities in the user's rate-later list
        - the recently recommended entities
        - completed by the all-time recommendations if needed

    Expected future updates:
        - use the user's preferred language(s) when retrieving the
          recommendations
    """

    max_suggestions = 20
    sample_size_pool1 = 9
    sample_size_pool2 = 7
    sample_size_pool3 = 4

    top_recommendations_limit = 400
    recent_recommendations_days = 30

    def _get_recommendations(self, entity_filters, exclude_ids: list[int]) -> list[int]:
        """
        Return the list of entity ids of all recommendations based on the
        provided filters.
        """
        poll = self.poll
        return (
            Entity.objects.filter_safe_for_poll(poll)
            .filter(**entity_filters)
            .exclude(id__in=exclude_ids)
            .values_list("id", flat=True)
        )

    def _get_compared_sufficiently(self, entity_filters) -> list[int]:
        """
        Return the list of entity ids that have been sufficiently compared by
        the user.
        """
        poll = self.poll
        user = self.user

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )

        return (
            ContributorRating.objects.filter(poll=poll, user=user)
            .filter(entity__in=Entity.objects.filter(**entity_filters))
            .annotate_n_comparisons()
            .filter(n_comparisons__gte=max_threshold)
            .values_list("entity_id", flat=True)
        )

    def _ids_from_pool_compared(self) -> list[int]:
        """
        Return a random list of entity ids that have been compared at least
        one time by the user, but strictly less than the user's setting
        `rate_later__auto_remove`.
        """
        poll = self.poll
        user = self.user

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )

        compared = (
            ContributorRating.objects.filter(poll=poll, user=user)
            .select_related("entity")
            .annotate_n_comparisons()
            .filter(n_comparisons__lt=max_threshold)
            .filter(n_comparisons__gt=0)
            .values_list("entity_id", flat=True)
        )

        return random.sample(
            # not a cryptographic use # nosec B311
            list(compared),
            min(len(compared), self.max_suggestions),
        )

    def _ids_from_pool_rate_later(self, exclude_ids: list[int]) -> list[int]:
        """
        Return a random list of entity ids from the user's rate-later list.
        """
        poll = self.poll
        user = self.user

        results = (
            RateLater.objects.filter(poll=poll, user=user)
            .exclude(entity_id__in=exclude_ids)
            .values_list("entity_id", flat=True)
        )

        return random.sample(
            # not a cryptographic use # nosec B311
            list(results),
            min(len(results), self.max_suggestions),
        )

    def _ids_from_pool_reco_last_month(self, exclude_ids: list[int]) -> list[int]:
        """
        Return random entity ids from the recent recommendations.

        Only ids of entities that have been compared fewer times than the
        user's setting `rate_later__auto_remove` are returned.
        """
        poll = self.poll

        entity_filters = {
            f"{poll.entity_cls.get_filter_date_field()}__gte": time_ago(
                days=self.recent_recommendations_days
            ).isoformat(),
        }

        if self.languages:
            entity_filters["metadata__language__in"] = self.languages

        recommendations = self._get_recommendations(entity_filters, exclude_ids)
        already_compared = self._get_compared_sufficiently(entity_filters)
        results = [reco for reco in recommendations if reco not in already_compared]

        return random.sample(
            # not a cryptographic use # nosec B311
            results,
            min(len(results), self.max_suggestions),
        )

    def _ids_from_pool_reco_all_time(self, exclude_ids: list[int]) -> list[int]:
        """
        Return random entity ids from the all-time top recommendations.

        Only ids of entities that have been compared fewer times than the
        user's setting `rate_later__auto_remove` are returned.
        """
        poll = self.poll

        entity_filters = {
            f"{poll.entity_cls.get_filter_date_field()}__lt": time_ago(
                days=self.recent_recommendations_days
            ).isoformat(),
        }

        if self.languages:
            entity_filters["metadata__language__in"] = self.languages

        recommendations = self._get_recommendations(entity_filters, exclude_ids)[
            : self.top_recommendations_limit
        ]
        already_compared = self._get_compared_sufficiently(entity_filters)
        results = [reco for reco in recommendations if reco not in already_compared]

        return random.sample(
            # not a cryptographic use # nosec B311
            results,
            min(len(results), self.max_suggestions),
        )

    def get_ids_from_pool1(self) -> list[int]:
        return self._ids_from_pool_compared()

    def get_ids_from_pool2(self, exclude_ids: list[int]) -> list[int]:
        return self._ids_from_pool_rate_later(exclude_ids)

    def get_ids_from_pool3(self, exclude_ids: list[int]) -> list[int]:
        return self._ids_from_pool_reco_last_month(exclude_ids)

    def get_ids_from_fallback_pool(self, exclude_ids: list[int], _: int) -> list[int]:
        return self._ids_from_pool_reco_all_time(exclude_ids)
