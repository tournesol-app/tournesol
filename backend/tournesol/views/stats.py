"""
API endpoints to show public statistics
"""
from dataclasses import dataclass
from typing import List

import logging

from django.utils import timezone
from core.utils.time import time_ago

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models import User
from tournesol.models import Comparison, Entity, Poll
from tournesol.serializers.stats import StatisticsSerializer


@dataclass
class ActiveUsersStatistics:
    total: int
    joined_last_month: int


@dataclass
class ComparedEntitiesStatistics:
    total: int
    added_last_month: int


@dataclass
class ComparisonsStatistics:
    total: int
    added_last_30_days: int
    added_current_week: int


@dataclass
class PollStatistics:
    name: str
    compared_entities: ComparedEntitiesStatistics
    comparisons: ComparisonsStatistics


class Statistics:
    """
    Representation of the Tournesol's public statistics.
    """

    active_users: ActiveUsersStatistics
    polls: List[PollStatistics]

    def __init__(self):
        self.active_users = ActiveUsersStatistics(0, 0)
        self.polls = []

    def set_active_users(self, user_count, last_month_user_count):
        self.active_users = ActiveUsersStatistics(user_count, last_month_user_count)

    def append_poll(
        self,
        poll_name: str,
        compared_entities_statistics: ComparedEntitiesStatistics,
        comparisons_statistics: ComparisonsStatistics,
    ):
        self.polls.append(
            PollStatistics(
                poll_name,
                compared_entities_statistics,
                comparisons_statistics,
            )
        )


@extend_schema_view(
    get=extend_schema(description="Fetch all Tournesol's public statistics.")
)
class StatisticsView(generics.GenericAPIView):
    """Return popularity statistics about Tournesol"""
    permission_classes = [AllowAny]
    serializer_class = StatisticsSerializer

    # _days_delta_week = timezone.now().day - time_ago(days=timezone.now().weekday()).day
    # print('DAYS DELTA WEEK:', _days_delta_week)
    _days_delta = 30 #make it 30 later
    # _days_delta_week = (datetime.now() - timedelta(days = datetime.now().weekday())).replace(hour=0, minute=0, second=0, microsecond=0)

    def get(self, request):
        statistics = Statistics()

        active_users = User.objects.filter(is_active=True).count()
        last_month_active_users = User.objects.filter(
            is_active=True, date_joined__gte=time_ago(days=self._days_delta)
        ).count()
        statistics.set_active_users(active_users, last_month_active_users)


        # mondayTime = (datetime.now() - timedelta(days = datetime.now().weekday())) #.replace(hour=0, minute=0, second=0, microsecond=0)
        daysParam = timezone.now().weekday()
        mondayDiff = time_ago(days=daysParam)
        hourParam, minuteParam, secondParam = mondayDiff.hour, mondayDiff.minute, mondayDiff.second

        for poll in Poll.objects.iterator():
            entities = Entity.objects.filter(type=poll.entity_type)
            compared_entities = entities.filter(rating_n_ratings__gt=0)
            compared_entity_count = compared_entities.count()
            last_month_compared_entity_count = compared_entities.filter(
                add_time__gte=time_ago(days=self._days_delta),
            ).count()

            compared_entities_statistics = ComparedEntitiesStatistics(
                compared_entity_count,
                last_month_compared_entity_count,
            )

            comparisons = Comparison.objects.filter(poll=poll)
            comparison_count = comparisons.count()
            # if len(comparisons) > 0:
            #     print("\n\nTimezone now:", timezone.now())
            #     print("\n\nlastWeek:", time_ago(days=daysParam, hours=hourParam, minutes=minuteParam, seconds=secondParam))
            #     print("\n\nMondayDiff:", mondayDiff, mondayDiff.day,daysParam, hourParam, minuteParam, secondParam)
            #     print("\n\nTimeago weekday:", timezone.now().weekday())
            #     print("\n\nComparison", comparisons[0])

            # We should optimize the following two calls so that they are called only when the server updates
            # the count, and not when the client calls this API
            last_month_comparison_count = comparisons.filter(
                datetime_lastedit__gte=time_ago(days=self._days_delta)
            ).count()
            current_week_comparison_count = comparisons.filter(
                datetime_lastedit__gte=time_ago(days=daysParam, hours=hourParam, minutes=minuteParam, seconds=secondParam)
            ).count()

            comparisons_statistics = ComparisonsStatistics(
                comparison_count,
                last_month_comparison_count,
                current_week_comparison_count
            )

            statistics.append_poll(
                poll.name,
                compared_entities_statistics,
                comparisons_statistics,
            )

        return Response(StatisticsSerializer(statistics).data)
