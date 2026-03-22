import random

from core.utils.time import time_ago
from tournesol.lib.suggestions.strategies.tocompare.classic import ClassicEntitySuggestionStrategy
from tournesol.models import ContributorRating, RateLater
from tournesol.models.rate_later import RATE_LATER_AUTO_REMOVE_DEFAULT


class WatchedEntitySuggestionStrategy(ClassicEntitySuggestionStrategy):
    """
    A variation of the strategy `ClassicEntitySuggestionStrategy` that
    suggests in priority entities that have been watched/consumed/understood.
    """

    sample_size_pool1 = 13
    sample_size_pool2 = 7
    sample_size_pool3 = 0

    def _ids_watched_and_compared(self) -> list[int]:
        poll = self.poll
        user = self.user

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )

        compared = (
            ContributorRating.objects.filter(poll=poll, user=user, entity_seen=True)
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

    def _ids_watched_and_rate_later(self, exclude_ids: list[int]) -> list[int]:
        poll = self.poll
        user = self.user

        # TODO: we could exclude entities that have been already compared more
        # than `RATE_LATER_AUTO_REMOVE_DEFAULT` times.
        query = """
            SELECT
              rate_later.id,
              rate_later.entity_id

            FROM tournesol_ratelater rate_later

            JOIN tournesol_contributorrating
              ON tournesol_contributorrating.poll_id = rate_later.poll_id
             AND tournesol_contributorrating.user_id = rate_later.user_id
             AND tournesol_contributorrating.entity_id = rate_later.entity_id

            WHERE rate_later.poll_id = %(poll_id)s
              AND rate_later.user_id = %(user_id)s
              AND tournesol_contributorrating.entity_seen = true
        """

        if exclude_ids:
            query += """
                AND rate_later.entity_id NOT IN %(exclude_ids)s
            """

        results = RateLater.objects.raw(
            query,
            {"poll_id": poll.id, "user_id": user.id, "exclude_ids": tuple(exclude_ids)},
        )

        samples = random.sample(
            # not a cryptographic use # nosec B311
            list(results),
            min(len(results), self.max_suggestions),
        )

        return [sample.id for sample in samples]

    def _ids_watched_and_reco_last_month(self, exclude_ids: list[int]) -> list[int]:
        poll = self.poll
        user = self.user

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )

        entity_filters = {
            f"{poll.entity_cls.get_filter_date_field()}__gte": time_ago(
                days=self.recent_recommendations_days
            ).isoformat(),
        }

        if self.languages:
            entity_filters["metadata__language__in"] = self.languages

        recommendations = self._get_recommendations(entity_filters, exclude_ids)
        already_compared = self._get_compared_sufficiently(entity_filters)

        watched = (
            ContributorRating.objects.filter(poll=poll, user=user, entity_seen=True)
            .select_related("entity")
            .annotate_n_comparisons()
            .filter(n_comparisons__lt=max_threshold)
            .values_list("entity_id", flat=True)
        )

        results = [
            reco for reco in recommendations if reco not in already_compared and reco in watched
        ]

        return random.sample(
            # not a cryptographic use # nosec B311
            results,
            min(len(results), self.max_suggestions),
        )

    def _ids_watched_and_reco_all_time(self, exclude_ids: list[int]) -> list[int]:
        poll = self.poll
        user = self.user

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )

        entity_filters = {
            f"{poll.entity_cls.get_filter_date_field()}__lt": time_ago(
                days=self.recent_recommendations_days
            ).isoformat(),
        }

        if self.languages:
            entity_filters["metadata__language__in"] = self.languages

        recommendations = self._get_recommendations(entity_filters, exclude_ids)
        already_compared = self._get_compared_sufficiently(entity_filters)

        watched = (
            ContributorRating.objects.filter(poll=poll, user=user, entity_seen=True)
            .select_related("entity")
            .annotate_n_comparisons()
            .filter(n_comparisons__lt=max_threshold)
            .values_list("entity_id", flat=True)
        )

        results = [
            reco for reco in recommendations if reco not in already_compared and reco in watched
        ]

        return random.sample(
            # not a cryptographic use # nosec B311
            results,
            min(len(results), self.max_suggestions),
        )

    def get_ids_from_pool1(self) -> list[int]:
        return self._ids_watched_and_compared()

    def get_ids_from_pool2(self, exclude_ids: list[int]) -> list[int]:
        return self._ids_watched_and_rate_later(exclude_ids)

    def get_ids_from_pool3(self, exclude_ids: list[int]) -> list[int]:
        return self._ids_watched_and_reco_last_month(exclude_ids)

    def get_ids_from_fallback_pool(self, exclude_ids: list[int]) -> list[int]:
        return self._ids_watched_and_reco_all_time(exclude_ids)
