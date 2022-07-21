"""
API endpoint to manipulate contributor's rate later list
"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.entities.base import UID_DELIMITER
from tournesol.entities.video import YOUTUBE_UID_NAMESPACE
from tournesol.models import Poll, RateLater
from tournesol.serializers.rate_later import RateLaterLegacySerializer


@extend_schema_view(
    post=extend_schema(
        responses={
            200: RateLaterLegacySerializer,
            409: OpenApiResponse(
                description="Conflict: the video is already in the rate later list,"
                " or there is an other error with the database query."
            ),
        }
    )
)
class RateLaterList(generics.ListCreateAPIView):
    """
    List all videos of a user's rate later list, or add a video to the list.
    """

    serializer_class = RateLaterLegacySerializer
    permission_classes = [IsAuthenticated]
    queryset = RateLater.objects.none()

    def get_queryset(self):
        return RateLater.objects.filter(user=self.request.user).prefetch_related("entity")


@extend_schema_view(
    get=extend_schema(description="Fetch a video from user's rate later list"),
    delete=extend_schema(description="Delete a video from user's rate later list"),
)
class RateLaterDetail(generics.RetrieveDestroyAPIView):
    """
    Retrieve, or delete a video from a user's rate later list.
    """

    serializer_class = RateLaterLegacySerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Fetch a given video or returns 404"""
        rate_later = get_object_or_404(
            RateLater,
            user__pk=self.request.user.pk,
            entity__uid=f'{YOUTUBE_UID_NAMESPACE}{UID_DELIMITER}{self.kwargs["video_id"]}',
            poll=Poll.default_poll()
        )
        return rate_later
