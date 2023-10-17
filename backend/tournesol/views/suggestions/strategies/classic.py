import numpy as np
from django.conf import settings
from django.db.models import Prefetch

from core.utils.time import time_ago
from tournesol.models import Entity, Poll, RateLater, EntityPollRating
from tournesol.serializers.suggestion import EntityFromRateLater, EntityFromPollRating

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

    def __init__(self, request, poll: Poll):
        super().__init__(request, poll)

        rng = np.random.default_rng()
        self.selected_pool = rng.random()

    def _entity_from_rate_later(self):
        poll = self.poll
        rate_later_size = RateLater.objects.filter(poll=poll, user=self.request.user).count()

        if not rate_later_size:
            return None

        return RateLater.objects.filter(poll=poll, user=self.request.user).prefetch_related(
            self.get_prefetch_entity_config()
        )[np.random.randint(0, rate_later_size)]

    def _entity_from_reco_last_month(self):
        # TODO: exclude compared entity according to setting rate_later__auto_remove
        poll = self.poll

        entity_filters = {
            "entity__{}__gte".format(poll.entity_cls.get_filter_date_field()): time_ago(
                days=30
            ).isoformat()
        }

        queryset = (
            EntityPollRating.objects.filter(
                poll=poll,
                sum_trust_scores__gte=settings.RECOMMENDATIONS_MIN_TRUST_SCORES,
                tournesol_score__gt=settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE,
            )
            .select_related("entity")
            .filter(**entity_filters)
        )

        count = queryset.count()
        if count:
            return queryset[np.random.randint(0, count)]

        return None

    def _entity_from_reco_all_time(self):
        # TODO: exclude compared entity according to setting rate_later__auto_remove
        # TODO: make the top 400 more explicit
        poll = self.poll

        queryset = (
            EntityPollRating.objects.filter(
                poll=poll,
                sum_trust_scores__gte=settings.RECOMMENDATIONS_MIN_TRUST_SCORES,
                tournesol_score__gt=settings.RECOMMENDATIONS_MIN_TOURNESOL_SCORE,
            ).select_related("entity")
        )[:400]

        count = queryset.count()
        if count:
            return queryset[np.random.randint(0, count)]

        return None

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
            entity = self._entity_from_rate_later()
            if entity:
                return entity

        # The remaining 22 % are divided equally between recent entities and
        # all entities. Note that all entities can include recent entities if
        # they are part of most recommended entities. This give a little
        # advantage to recent entities.
        if self.selected_pool < 0.89:
            entity = self._entity_from_reco_last_month()
            if entity:
                return entity

        entity = self._entity_from_reco_all_time()
        if entity:
            return entity

        return None

    def get_result_advanced_user(self):
        raise NotImplementedError
