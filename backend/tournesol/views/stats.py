"""
API endpoints to show public statistics
"""

from datetime import datetime, timedelta

from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view


from core.models import User
from ..models import Video, Comparison

@extend_schema_view(
    get=extend_schema(
        description="Retrieve statistics"
    )
)
class StatisticsView(APIView):
    permission_classes = [AllowAny]

    # Query Set definition
    user_queryset = User.objects.all().count()
    last_month_user_queryset = User.objects.filter(
            date_joined__gte=datetime.today() - timedelta(days=30)
        ).count()
    video_queryset = Video.objects.all().count()
    last_month_video_queryset = Video.objects.filter(
            publication_date__gte=datetime.today() - timedelta(days=30)
        ).count()
    comparison_queryset = Comparison.objects.all().count()
    last_month_comparison_queryset = Comparison.objects.filter(
            datetime_lastedit__gte=datetime.today() - timedelta(days=30)
        ).count()

    def get(self, request, format=None):
        return Response({
            "user_count": self.user_queryset,
            "last_month_user_count": self.last_month_user_queryset,
            "video_count": self.video_queryset,
            "last_month_video_count": self.last_month_video_queryset,
            "comparison_count": self.comparison_queryset,
            "last_month_comparaison_count": self.last_month_video_queryset
            }
        )
