import numpy as np
from django.db.models import Prefetch

from tournesol.models import Entity, Poll, RateLater

from .base import ContributionSuggestionStrategy


class ClassicEntitySuggestionStrategy(ContributionSuggestionStrategy):
    """
    A contribution strategy that will suggest a random entity to compare.

    The entity is retrieved from the following pools:
        - user's rate-later list
        - last month recommendations
        - all time recommendations
    """

    def _entity_from_rate_later(self):
        poll = self.poll
        rate_later_size = RateLater.objects.filter(poll=poll, user=self.request.user).count()

        if not rate_later_size:
            return None

        return RateLater.objects.filter(poll=poll, user=self.request.user).prefetch_related(
            self.get_prefetch_entity_config()
        )[np.random.randint(0, rate_later_size)]

    def _entity_from_reco_last_month(self):
        return 0

    def _entity_from_reco_all_time(self):
        return 0

    def get_prefetch_entity_config(self):
        poll = self.poll
        return Prefetch(
            "entity",
            queryset=(
                Entity.objects.with_prefetched_poll_ratings(
                    poll_name=poll.name
                ).with_prefetched_contributor_ratings(poll=poll, user=self.request.user)
            ),
        )

    def get_result(self):
        entity = self._entity_from_rate_later()
        if entity:
            return entity

        entity = self._entity_from_reco_last_month()
        if entity:
            return entity

        entity = self._entity_from_reco_all_time()
        if entity:
            return entity

        return None
