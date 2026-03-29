from abc import abstractmethod
from dataclasses import dataclass

from tournesol.lib.suggestions.strategies.base import ContributionSuggestionStrategy
from tournesol.models import Entity


@dataclass
class IdPool:
    ids: list[int]
    sample_size: int


class PoolBasedEntitySuggestionStrategy(ContributionSuggestionStrategy):
    """
    Abstract Base Class based on three entity pools to suggest entities to
    compare.
    """

    # The maximum number of results returned by the strategy.
    max_suggestions = 20

    # The expected number of entities retrieved from each pool. The sum should
    # match the `max_suggestions`.
    sample_size_pool1 = 9
    sample_size_pool2 = 7
    sample_size_pool3 = 4

    def _consolidate_pools(self, pool1: IdPool, pool2: IdPool, pool3: IdPool) -> list[int]:
        """
        Return a consolidated list of elements from all provided pools.

        A list is considered consolidated when its population size is equals,
        or is as close as possible, to the sum of all pool's sample sizes.
        """
        extra_sample1 = 0
        extra_sample2 = 0

        free_slots_in_pool1 = pool1.sample_size - len(pool1.ids[: pool1.sample_size])
        free_slots_in_pool2 = pool2.sample_size - len(pool2.ids[: pool2.sample_size])

        # If the pool 1 contains fewer ids than expected, try to pick more
        # ids from the pools 2.
        if free_slots_in_pool1 > 0:
            extra_sample2 = free_slots_in_pool1

        # If the pool 2 contains fewer ids than expected, try to pick more
        # ids from the pool 1.
        if free_slots_in_pool2 > 0:
            extra_sample1 = free_slots_in_pool2

        sample1 = pool1.ids[: pool1.sample_size + extra_sample1]
        sample2 = pool2.ids[: pool2.sample_size + extra_sample2]
        sample3 = pool3.ids[: pool3.sample_size]

        free_slots = self.max_suggestions - len(sample1) - len(sample2) - len(sample3)

        if free_slots > 0:
            extra_sample3 = free_slots // 2

            if free_slots % 2 == 1:
                extra_sample3 += 1

            sample3 = pool3.ids[: pool3.sample_size + extra_sample3]

        return sample1 + sample2 + sample3

    def _get_consolidated_results(self):
        poll = self.poll

        pool1 = self.get_ids_from_pool1()
        pool2 = self.get_ids_from_pool2(pool1)
        pool3 = self.get_ids_from_pool3(pool1 + pool2)

        sample1_size = len(pool1[: self.sample_size_pool1])
        sample2_size = len(pool2[: self.sample_size_pool2])
        sample3_size = len(pool3[: self.sample_size_pool3])

        if sample1_size + sample2_size + sample3_size >= self.max_suggestions:
            return (
                Entity.objects.filter(
                    id__in=pool1[: self.sample_size_pool1]
                    + pool2[: self.sample_size_pool2]
                    + pool3[: self.sample_size_pool3]
                )
                .with_prefetched_poll_ratings(poll_name=poll.name)
                .order_by("?")
            )

        # Allow the empty slots from the first pool to be filled by the
        # items of the second pool and vice-versa.
        results = self._consolidate_pools(
            IdPool(pool1, self.sample_size_pool1),
            IdPool(pool2, self.sample_size_pool2),
            IdPool(pool3, self.sample_size_pool3),
        )

        free_slots = self.max_suggestions - len(results)

        if free_slots > 0:
            last_resort = self.get_ids_from_fallback_pool(results, free_slots)
            results += last_resort[:free_slots]

        return (
            Entity.objects.filter(id__in=results)
            .with_prefetched_poll_ratings(poll_name=poll.name)
            .order_by("?")
        )

    @abstractmethod
    def get_ids_from_pool1(self) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def get_ids_from_pool2(self, exclude_ids: list[int]) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def get_ids_from_pool3(self, exclude_ids: list[int]) -> list[int]:
        raise NotImplementedError

    @abstractmethod
    def get_ids_from_fallback_pool(self, exclude_ids: list[int], free_slots: int) -> list[int]:
        raise NotImplementedError

    def get_results(self):
        return self._get_consolidated_results()
