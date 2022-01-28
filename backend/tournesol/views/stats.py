"""
API endpoints to show public statistics
"""

from datetime import datetime, timedelta

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import exceptions, generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from core.models import User

from ..models import Comparison, Video
from ..serializers import StatisticsSerializer


class Statistics:
    def add_user_statistics(self, user_count, last_month_user_count):
        self.user_count = user_count
        self.last_month_user_count = last_month_user_count

    def add_video_statistics(self, video_count, last_month_video_count):
        self.video_count = video_count
        self.last_month_video_count = last_month_video_count

    def add_comparison_statistics(self, comparison_count, last_month_comparison_count):
        self.comparison_count = comparison_count
        self.last_month_comparison_count = last_month_comparison_count


@extend_schema_view(
    get=extend_schema(
        description="Retrieve statistics"
    )
)
class StatisticsView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    serializer_class = StatisticsSerializer
    _days_delta = 30

    def get(self, request):
        # Query definition
        user_count = User.objects.all().count()
        last_month_user_count = User.objects.filter(
                date_joined__gte=datetime.today() - timedelta(days=self._days_delta)
            ).count()
        video_count = Video.objects.all().count()
        last_month_video_count = Video.objects.filter(
                publication_date__gte=datetime.today() - timedelta(days=self._days_delta)
            ).count()
        comparison_count = Comparison.objects.all().count()
        last_month_comparison_count = Comparison.objects.filter(
                datetime_lastedit__gte=datetime.today() - timedelta(days=self._days_delta)
            ).count()

        statistics = Statistics()
        statistics.add_user_statistics(user_count, last_month_user_count)
        statistics.add_video_statistics(video_count, last_month_video_count)
        statistics.add_comparison_statistics(comparison_count, last_month_comparison_count)

        return Response(StatisticsSerializer(statistics).data)
