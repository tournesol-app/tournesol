import random
from dataclasses import dataclass

from django.conf import settings

from core.utils.time import time_ago
from tournesol.models import ContributorRating, EntityPollRating, RateLater
from tournesol.models.rate_later import RATE_LATER_AUTO_REMOVE_DEFAULT
from tournesol.serializers.suggestion import ResultFromPollRating

from .base import ContributionSuggestionStrategy


@dataclass
class UIDsPool:
    uids: list[int]
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

    def _uids_from_pool_compared(self) -> list[int]:
        poll = self.poll
        user = self.request.user

        max_threshold = user.settings.get(poll.name, {}).get(
            "rate_later__auto_remove", RATE_LATER_AUTO_REMOVE_DEFAULT
        )

        compared = (
            ContributorRating.objects.filter(poll=poll, user=user)
            .select_related("entity")
            .annotate_n_comparisons()
            .filter(n_comparisons__lt=max_threshold)
            .values_list("entity_id", flat=True)
        )

        return random.sample(list(compared), min(len(compared), self.max_suggestions))

    def _uids_from_pool_rate_later(self, exclude_uids: list[int]) -> list[int]:
        """
        Return random UIDs from the user's rate-later list.
        """
        poll = self.poll
        user = self.request.user

        results = (
            RateLater.objects.filter(poll=poll, user=user)
            .exclude(entity_id__in=exclude_uids)
            .values_list("entity_id", flat=True)
        )

        return random.sample(list(results), min(len(results), self.max_suggestions))

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

        return random.sample(results, min(size, self.max_suggestions))

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

        return random.sample(results, min(size, self.max_suggestions))

    def _consolidate_results(self, pool1: UIDsPool, pool2: UIDsPool, pool3: UIDsPool):
        """
        Return a consolidated list of elements from all provided pools.

        A list is considered consolidated when its population size is equals,
        or as close as possible, to the sum of all pool's sample sizes.
        """
        extra_sample2 = 0
        extra_sample3 = 0

        free_slots_in_pool1 = pool1.sample_size - len(pool1.uids[: pool1.sample_size])
        free_slots_in_pool2 = pool2.sample_size - len(pool2.uids[: pool2.sample_size])
        free_slots_in_pool3 = pool3.sample_size - len(pool3.uids[: pool3.sample_size])

        # If the pool 1 contains less UIDs than expected, try to pick more
        # UIDs from the pools 2 and 3.
        if free_slots_in_pool1 > 0:
            extra_sample2 = free_slots_in_pool1 // 2
            extra_sample3 = free_slots_in_pool1 // 2

            if free_slots_in_pool1 % 2 == 1:
                extra_sample2 += 1

        sample1 = pool1.uids[: pool1.sample_size]

        # If the pool 3 contains less UIDs than expected, try to pick more
        # UIDs from the pool 2.
        if free_slots_in_pool3 > 0:
            extra_sample2 += extra_sample3 + free_slots_in_pool3

        sample2 = pool2.uids[: pool2.sample_size + extra_sample2]

        # If the pool 2 contains less UIDs than expected, try to pick more
        # UIDs from the pool 3.
        if free_slots_in_pool2 > 0:
            extra_sample3 += extra_sample2 + free_slots_in_pool2

        sample3 = pool3.uids[: pool3.sample_size + extra_sample3]

        free_slots = self.max_suggestions - len(sample1) - len(sample2) - len(sample3)

        # In case of need, add more UIDs from the pool 1.
        if free_slots > 0:
            sample1 = pool1.uids[: pool1.sample_size + free_slots]

        return sample1 + sample2 + sample3

    def get_serializer_class(self):
        return ResultFromPollRating

    def get_results(self):
        return self.get_result_for_user_intermediate()

    def get_result_for_user_new(self):
        raise NotImplementedError

    def get_result_for_user_intermediate(self):
        poll = self.poll

        pool1 = self._uids_from_pool_compared()
        pool2 = self._uids_from_pool_rate_later(pool1)
        pool3 = self._uids_from_pool_reco_last_month(pool1 + pool2)

        sample1_size = len(pool1[: self.sample_size_compared])
        sample2_size = len(pool2[: self.sample_size_rate_later])
        sample3_size = len(pool3[: self.sample_size_reco_last_month])

        if sample1_size + sample2_size + sample3_size >= self.max_suggestions:
            return (
                EntityPollRating.objects.filter(
                    poll=poll,
                )
                .select_related("entity")
                .filter(entity_id__in=pool1 + pool2 + pool3)
            )

        # This optional step allows the empty slots from a pool to be filled
        # by additional UIDs from other pools. The UIDs from the top
        # recommendations are used as a last resort, only if the current pools
        # are not able to provide enough UIDs by themselves.
        results = self._consolidate_results(
            UIDsPool(pool1, self.sample_size_compared),
            UIDsPool(pool2, self.sample_size_rate_later),
            UIDsPool(pool3, self.sample_size_reco_last_month),
        )

        free_slots = self.max_suggestions - len(results)

        if free_slots > 0:
            last_resort = self._uids_from_pool_reco_all_time(results)
            results += last_resort[:free_slots]

        return (
            EntityPollRating.objects.filter(
                poll=poll,
            )
            .select_related("entity")
            .filter(entity_id__in=results)
        )

    def get_result_for_user_advanced(self):
        raise NotImplementedError
