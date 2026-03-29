import random
from typing import Optional

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
        """
        Return a random list of entity ids that have been watched and compared
        at least one time by the user, but strictly less than the user's setting
        `rate_later__auto_remove`.
        """
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
        """
        Return a random list of entity ids that have been watched and are
        currently in the user's rate-later list.
        """
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

    def _ids_watched_and_recommended(
        self,
        exclude_ids: list[int],
        entity_filters: dict[str, str],
        limit: Optional[int] = None,
    ) -> list[int]:
        """
        Return random entity ids from the recommendations that have been
        watched by the user.

        Only ids of entities that have been compared fewer times than the
        user's setting `rate_later__auto_remove` are returned.

        Use `entity_filters` to return more or less recent recommendations.
        """
        poll = self.poll
        user = self.user

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )

        if self.languages:
            entity_filters["metadata__language__in"] = self.languages

        recommendations = self._get_recommendations(entity_filters, exclude_ids)
        if limit:
            recommendations = recommendations[:limit]

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

    def _ids_watched_and_reco_last_month(self, exclude_ids: list[int]) -> list[int]:
        poll = self.poll
        entity_filters = {
            f"{poll.entity_cls.get_filter_date_field()}__gte": time_ago(
                days=self.recent_recommendations_days
            ).isoformat(),
        }

        return self._ids_watched_and_recommended(exclude_ids, entity_filters)

    def _ids_watched_and_reco_all_time(self, exclude_ids: list[int]) -> list[int]:
        poll = self.poll
        entity_filters = {
            f"{poll.entity_cls.get_filter_date_field()}__lt": time_ago(
                days=self.recent_recommendations_days
            ).isoformat(),
        }

        return self._ids_watched_and_recommended(
            exclude_ids, entity_filters, self.top_recommendations_limit
        )

    def get_ids_from_pool1(self) -> list[int]:
        return self._ids_watched_and_compared()

    def get_ids_from_pool2(self, exclude_ids: list[int]) -> list[int]:
        return self._ids_watched_and_rate_later(exclude_ids)

    def get_ids_from_pool3(self, exclude_ids: list[int]) -> list[int]:
        return self._ids_watched_and_reco_last_month(exclude_ids)

    def get_ids_from_fallback_pool(self, exclude_ids: list[int], free_slots: int) -> list[int]:
        watched_ids = self._ids_watched_and_reco_all_time(exclude_ids)

        if len(watched_ids) >= free_slots:
            return watched_ids

        classic_strategy = ClassicEntitySuggestionStrategy(self.poll, self.user, self.languages)

        free_slots -= len(watched_ids)
        pool1 = classic_strategy.get_ids_from_pool1()

        if len(pool1) >= free_slots:
            return watched_ids + pool1

        free_slots -= len(pool1)
        pool2 = classic_strategy.get_ids_from_pool2(exclude_ids + watched_ids + pool1)

        if len(pool2) >= free_slots:
            return watched_ids + pool1 + pool2

        free_slots -= len(pool2)
        pool3 = classic_strategy.get_ids_from_pool3(exclude_ids + watched_ids + pool1 + pool2)

        if len(pool3) >= free_slots:
            return watched_ids + pool1 + pool2 + pool3

        free_slots -= len(pool3)
        last_resort = classic_strategy.get_ids_from_fallback_pool(
            exclude_ids + watched_ids + pool1 + pool2 + pool3, free_slots
        )
        return watched_ids + pool1 + pool2 + pool3 + last_resort
