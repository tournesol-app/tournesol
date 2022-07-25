"""
API endpoints to show public statistics
"""
from typing import List

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models import User
from core.utils.time import time_ago
from tournesol.models import Comparison, Entity, Poll
from tournesol.serializers.stats import StatisticsSerializer


class ActiveUsersStatistics:
    def __init__(self, total, joined_last_month):
        self.total = total
        self.joined_last_month = joined_last_month


class ComparedEntitiesStatistics:
    def __init__(self, total, added_last_month):
        self.total = total
        self.added_last_month = added_last_month


class ComparisonsStatistics:
    def __init__(self, total, added_last_month):
        self.total = total
        self.added_last_month = added_last_month


class PollStatistics:
    def __init__(
        self,
        name,
        compared_entity_count,
        last_month_compared_entity_count,
        comparison_count,
        last_month_comparison_count,
    ):
        self.name = name
        self.compared_entities = ComparedEntitiesStatistics(
            compared_entity_count, last_month_compared_entity_count
        )
        self.comparisons = ComparisonsStatistics(
            comparison_count, last_month_comparison_count
        )


class Statistics:
    """
    Representation of the Tournesol's public statistics.
    """

    active_users: ActiveUsersStatistics
    polls: List[PollStatistics]

    def __init__(self):
        self.active_users = 0
        self.polls = []

    def set_active_users(self, user_count, last_month_user_count):
        self.active_users = ActiveUsersStatistics(user_count, last_month_user_count)

    def append_poll(
        self,
        poll_name,
        compared_entity_count,
        last_month_compared_entity_count,
        comparison_count,
        last_month_comparison_count,
    ):
        self.polls.append(
            PollStatistics(
                poll_name,
                compared_entity_count,
                last_month_compared_entity_count,
                comparison_count,
                last_month_comparison_count,
            )
        )


@extend_schema_view(
    get=extend_schema(description="Fetch all Tournesol's public statistics.")
)
class StatisticsView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = StatisticsSerializer

    _days_delta = 30

    def get(self, request):
        statistics = Statistics()

        active_users = User.objects.filter(is_active=True).count()
        last_month_active_users = User.objects.filter(
            is_active=True, date_joined__gte=time_ago(days=self._days_delta)
        ).count()
        statistics.set_active_users(active_users, last_month_active_users)

        for poll in Poll.objects.iterator():
            entities = Entity.objects.filter(type=poll.entity_type)
            compared_entities = entities.filter(rating_n_ratings__gt=0)
            compared_entity_count = compared_entities.count()
            last_month_compared_entity_count = compared_entities.filter(
                add_time__gte=time_ago(days=self._days_delta),
            ).count()

            comparisons = Comparison.objects.filter(poll=poll)
            comparison_count = comparisons.count()
            last_month_comparison_count = comparisons.filter(
                datetime_lastedit__gte=time_ago(days=self._days_delta)
            ).count()

            statistics.append_poll(
                poll.name,
                compared_entity_count,
                last_month_compared_entity_count,
                comparison_count,
                last_month_comparison_count,
            )

        return Response(StatisticsSerializer(statistics).data)
