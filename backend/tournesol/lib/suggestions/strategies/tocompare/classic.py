import random
from dataclasses import dataclass

from django.conf import settings

from core.utils.time import time_ago
from tournesol.lib.suggestions.strategies.base import ContributionSuggestionStrategy
from tournesol.models import ContributorRating, Entity, EntityPollRating, RateLater
from tournesol.models.rate_later import RATE_LATER_AUTO_REMOVE_DEFAULT
from tournesol.serializers.suggestion import EntityToCompare


@dataclass
class IdPool:
    ids: list[int]
    sample_size: int


class ClassicEntitySuggestionStrategy(ContributionSuggestionStrategy):
    """
    A contribution strategy that will suggest random entities to compare.

    The entity are retrieved from the following pools:
        - entities already compared by the users
        - entities in the user's rate-later list
        - the recent recommendations
        - completed by the top recommendations if needed

    Expected future updates:
        - use the user's preferred language(s)
    """

    # The maximum number of results returned by the strategy.
    max_suggestions = 20

    # The expected number of entities retrieved from each pool.
    sample_size_compared = 9
    sample_size_rate_later = 7
    sample_size_reco_last_month = 4

    top_recommendations_limit = 400
    recent_recommendations_days = 30

    def _get_recommendations(self, entity_filters, exclude_ids: list[int]) -> list[int]:
        """
        Return all entity ids of all recommendations based on the provided
        filters.
        """
        poll = self.poll

        return (
            EntityPollRating.objects.filter(
                poll=poll,
                sum_trust_scores__gte=settings.RECOMMENDATIONS_MIN_TRUST_SCORES,
                tournesol_score__gt=settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE,
            )
            .select_related("entity")
            .filter(**entity_filters)
            .exclude(entity_id__in=exclude_ids)
            .values_list("entity_id", flat=True)
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
            .select_related("entity")
            .filter(**entity_filters)
            .annotate_n_comparisons()
            .filter(n_comparisons__gte=max_threshold)
            .values_list("entity_id", flat=True)
        )

    def _ids_from_pool_compared(self) -> list[int]:
        """
        Return random list of entity ids that have been compared at least one
        time by the user, but less than the user's setting
        `rate_later__auto_remove` times.
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

        return random.sample(list(compared), min(len(compared), self.max_suggestions))

    def _ids_from_pool_rate_later(self, exclude_ids: list[int]) -> list[int]:
        """
        Return a random list entity ids from the user's rate-later list.
        """
        poll = self.poll
        user = self.user

        results = (
            RateLater.objects.filter(poll=poll, user=user)
            .exclude(entity_id__in=exclude_ids)
            .values_list("entity_id", flat=True)
        )

        return random.sample(list(results), min(len(results), self.max_suggestions))

    def _ids_from_pool_reco_last_month(self, exclude_ids: list[int]) -> list[int]:
        """
        Return random ids from the recent recommendations.

        Only ids of entities that have been compared fewer times than the
        user's setting `rate_later__auto_remove` are returned.
        """
        poll = self.poll

        entity_filters = {
            f"entity__{poll.entity_cls.get_filter_date_field()}__gte": time_ago(
                days=self.recent_recommendations_days
            ).isoformat(),
        }

        recommendations = self._get_recommendations(entity_filters, exclude_ids)
        already_compared = self._get_compared_sufficiently(entity_filters)
        results = [reco for reco in recommendations if reco not in already_compared]

        return random.sample(results, min(len(results), self.max_suggestions))

    def _ids_from_pool_reco_all_time(self, exclude_ids: list[int]) -> list[int]:
        """
        Return random ids from the top recommendations.

        Only ids of entities that have been compared fewer times than the
        user's setting `rate_later__auto_remove` are returned.
        """
        poll = self.poll

        entity_filters = {
            f"entity__{poll.entity_cls.get_filter_date_field()}__lt": time_ago(
                days=self.recent_recommendations_days
            ).isoformat(),
        }

        recommendations = self._get_recommendations(entity_filters, exclude_ids)[
            : self.top_recommendations_limit
        ]
        already_compared = self._get_compared_sufficiently(entity_filters)
        results = [reco for reco in recommendations if reco not in already_compared]

        return random.sample(results, min(len(results), self.max_suggestions))

    def _consolidate_results(self, pool1: IdPool, pool2: IdPool, pool3: IdPool):
        """
        Return a consolidated list of elements from all provided pools.

        A list is considered consolidated when its population size is equals,
        or is as close as possible, to the sum of all pool's sample sizes.
        """
        extra_sample2 = 0
        extra_sample3 = 0

        free_slots_in_pool1 = pool1.sample_size - len(pool1.ids[: pool1.sample_size])
        free_slots_in_pool2 = pool2.sample_size - len(pool2.ids[: pool2.sample_size])
        free_slots_in_pool3 = pool3.sample_size - len(pool3.ids[: pool3.sample_size])

        # If the pool 1 contains fewer ids than expected, try to pick more
        # ids from the pools 2 and 3.
        if free_slots_in_pool1 > 0:
            extra_sample2 = free_slots_in_pool1 // 2
            extra_sample3 = free_slots_in_pool1 // 2

            if free_slots_in_pool1 % 2 == 1:
                extra_sample2 += 1

        sample1 = pool1.ids[: pool1.sample_size]

        # If the pool 3 contains fewer ids than expected, try to pick more
        # ids from the pool 2.
        if free_slots_in_pool3 > 0:
            extra_sample2 += extra_sample3 + free_slots_in_pool3

        sample2 = pool2.ids[: pool2.sample_size + extra_sample2]

        # If the pool 2 contains fewer ids than expected, try to pick more
        # ids from the pool 3.
        if free_slots_in_pool2 > 0:
            extra_sample3 += extra_sample2 + free_slots_in_pool2

        sample3 = pool3.ids[: pool3.sample_size + extra_sample3]

        free_slots = self.max_suggestions - len(sample1) - len(sample2) - len(sample3)

        # In case of need, add more ids from the pool 1.
        if free_slots > 0:
            sample1 = pool1.ids[: pool1.sample_size + free_slots]

        return sample1 + sample2 + sample3

    def get_serializer_class(self):
        return EntityToCompare

    def get_results(self):
        return self.get_result_for_user_intermediate()

    def get_result_for_user_new(self):
        raise NotImplementedError

    def get_result_for_user_intermediate(self):
        poll = self.poll

        pool1 = self._ids_from_pool_compared()
        pool2 = self._ids_from_pool_rate_later(pool1)
        pool3 = self._ids_from_pool_reco_last_month(pool1 + pool2)

        sample1_size = len(pool1[: self.sample_size_compared])
        sample2_size = len(pool2[: self.sample_size_rate_later])
        sample3_size = len(pool3[: self.sample_size_reco_last_month])

        if sample1_size + sample2_size + sample3_size >= self.max_suggestions:
            return Entity.objects.filter(
                id__in=pool1 + pool2 + pool3
            ).with_prefetched_poll_ratings(poll_name=poll.name)

        # This optional step allows the empty slots from a pool to be filled
        # by additional ids from other pools. The ids from the top
        # recommendations are used as a last resort, only if the current pools
        # are not able to provide enough ids by themselves.
        results = self._consolidate_results(
            IdPool(pool1, self.sample_size_compared),
            IdPool(pool2, self.sample_size_rate_later),
            IdPool(pool3, self.sample_size_reco_last_month),
        )

        free_slots = self.max_suggestions - len(results)

        if free_slots > 0:
            last_resort = self._ids_from_pool_reco_all_time(results)
            results += last_resort[:free_slots]

        return Entity.objects.filter(id__in=results).with_prefetched_poll_ratings(
            poll_name=poll.name
        )

    def get_result_for_user_advanced(self):
        raise NotImplementedError
