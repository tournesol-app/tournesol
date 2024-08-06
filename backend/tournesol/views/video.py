"""
API endpoint to manipulate videos
"""

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import GenericViewSet

from tournesol.entities.video import TYPE_VIDEO
from tournesol.models import Entity
from tournesol.serializers.entity import VideoSerializer
from tournesol.throttling import (
    BurstAnonRateThrottle,
    BurstUserRateThrottle,
    PostScopeRateThrottle,
    SustainedAnonRateThrottle,
    SustainedUserRateThrottle,
)


@extend_schema_view(
    create=extend_schema(
        description="Add a video to the db if it does not already exist."
    ),
)
class VideoViewSet(
    mixins.CreateModelMixin,
    GenericViewSet,
):
    """Obsolete view for video recommendations."""
    queryset = Entity.objects.filter(type=TYPE_VIDEO)
    permission_classes = [IsAuthenticated]
    serializer_class = VideoSerializer

    throttle_classes = [
        PostScopeRateThrottle,
        BurstAnonRateThrottle,
        BurstUserRateThrottle,
        SustainedAnonRateThrottle,
        SustainedUserRateThrottle,
    ]

    throttle_scope = "api_video_post"

    def perform_create(self, serializer):
        entity = serializer.save()
        entity.single_poll_ratings = []
