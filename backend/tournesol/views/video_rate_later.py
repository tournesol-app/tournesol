"""
API endpoint to manipulate contributor's rate later list
"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.models import VideoRateLater
from tournesol.serializers.video_rate_later import VideoRateLaterSerializer


@extend_schema_view(
    post=extend_schema(
        responses={
            200: VideoRateLaterSerializer,
            409: OpenApiResponse(
                description="Conflict: the video is already in the rate later list,"
                " or there is an other error with the database query."
            ),
        }
    )
)
class VideoRateLaterList(generics.ListCreateAPIView):
    """
    List all videos of a user's rate later list, or add a video to the list.
    """

    serializer_class = VideoRateLaterSerializer
    permission_classes = [IsAuthenticated]
    queryset = VideoRateLater.objects.none()

    def get_queryset(self):
        return VideoRateLater.objects.filter(user=self.request.user)


@extend_schema_view(
    get=extend_schema(description="Fetch a video from user's rate later list"),
    delete=extend_schema(description="Delete a video from user's rate later list"),
)
class VideoRateLaterDetail(generics.RetrieveDestroyAPIView):
    """
    Retrieve, or delete a video from a user's rate later list.
    """

    serializer_class = VideoRateLaterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Fetch a given video or returns 404"""
        video_rate_later = get_object_or_404(
            VideoRateLater,
            user__pk=self.request.user.pk,
            video__video_id=self.kwargs["video_id"],
        )
        return video_rate_later
