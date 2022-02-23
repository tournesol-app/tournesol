"""
API endpoints to show public statistics
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from core.models import User
from core.utils.time import time_ago
from tournesol.serializers.stats import StatisticsSerializer

from ..models import Comparison, Entity


class Statistics:
    """
    Representation of a Statistics
    """

    def add_user_statistics(self, user_count, last_month_user_count):
        self.user_count = user_count
        self.last_month_user_count = last_month_user_count

    def add_video_statistics(self, video_count, last_month_video_count):
        self.video_count = video_count
        self.last_month_video_count = last_month_video_count

    def add_comparison_statistics(self, comparison_count, last_month_comparison_count):
        self.comparison_count = comparison_count
        self.last_month_comparison_count = last_month_comparison_count


@extend_schema_view(get=extend_schema(description="Retrieve statistics."))
class StatisticsView(generics.GenericAPIView):
    """
    API view for retrieving statistics
    """

    permission_classes = [AllowAny]

    serializer_class = StatisticsSerializer
    _days_delta = 30

    def get(self, request):
        # Query definition
        user_count = User.objects.filter(is_active=True).count()
        last_month_user_count = User.objects.filter(
            is_active=True, date_joined__gte=time_ago(days=self._days_delta)
        ).count()
        video_count = Entity.objects.filter(rating_n_ratings__gt=0).count()
        last_month_video_count = Entity.objects.filter(
            add_time__gte=time_ago(days=self._days_delta), rating_n_ratings__gt=0
        ).count()
        comparison_count = Comparison.objects.all().count()
        last_month_comparison_count = Comparison.objects.filter(
            datetime_lastedit__gte=time_ago(days=self._days_delta)
        ).count()

        statistics = Statistics()
        statistics.add_user_statistics(user_count, last_month_user_count)
        statistics.add_video_statistics(video_count, last_month_video_count)
        statistics.add_comparison_statistics(
            comparison_count, last_month_comparison_count
        )

        return Response(StatisticsSerializer(statistics).data)
