"""
API endpoint to manipulate contributor's rate later list
"""

from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework import generics, mixins, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiResponse

from ..models import Video, VideoRateLater
from ..serializers import VideoRateLaterSerializer


class VideoRateLaterList(
    mixins.ListModelMixin, generics.GenericAPIView
):
    """
    List all videos of a user's rate later list, or add a video to the list.
    """

    serializer_class = VideoRateLaterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VideoRateLater.objects.filter(user=self.request.user)

    def get(self, request, *args, **kwargs):
        """API call to return list of rate_later videos"""
        return self.list(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: VideoRateLaterSerializer,
            404: OpenApiResponse(
                description="Not Found: the video doesn't exist in the database."
            ),
            409: OpenApiResponse(
                description="Conflict: the video is already in the rate later list,"
                            " or there is an other error with the database query."
            )
        }
    )
    def post(self, request, *args, **kwargs):
        """
        Add an existing video to a user's rate later list.
        """
        try:
            video = get_object_or_404(Video, video_id=request.data["video"]["video_id"])
        except KeyError:
            return Response(
                {
                    "detail": "Required field video.video_id not found.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        video_rate_later = VideoRateLater(user=request.user, video=video)

        try:
            video_rate_later.save()
        except IntegrityError:
            return Response({"detail": "409 Conflict"}, status=status.HTTP_409_CONFLICT)

        return Response(VideoRateLaterSerializer(video_rate_later).data)


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
