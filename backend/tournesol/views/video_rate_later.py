"""
API endpoint to manipulate contributor's rate later list
"""

from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework import generics, mixins, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from ..models import Video, VideoRateLater
from ..serializers import VideoRateLaterSerializer


def verify_username(request, username):
    """ Fails if username is different from request.user """
    if request.user.username != username:
        raise PermissionDenied("403 Forbidden")


class VideoRateLaterList(
    mixins.ListModelMixin, generics.GenericAPIView
):
    """
    List all videos of a user's rate later list, or add a video to the list.
    """

    serializer_class = VideoRateLaterSerializer

    def get_queryset(self):
        return VideoRateLater.objects.filter(user__username=self.kwargs["username"])

    def get(self, request, *args, **kwargs):
        """API call to return list of rate_later videos"""
        verify_username(request, kwargs["username"])
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Add an existing video to a user's rate later list.

        Status code:

            403 Forbidden
                the logged user is not the target user

            404 Not Found
                the video doesn't exist in the database

            409 Conflict
                 the video is already in the rate later list
                 or there is an other error with the database request
        """
        verify_username(request, kwargs["username"])

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


class VideoRateLaterDetail(
    mixins.RetrieveModelMixin, mixins.DestroyModelMixin, generics.GenericAPIView
):
    """
    Retrieve, or delete a video from a user's rate later list.
    """

    serializer_class = VideoRateLaterSerializer

    def get_object(self):
        """Fetch a given video or returns 404"""
        video_rate_later = get_object_or_404(
            VideoRateLater,
            user__pk=self.request.user.pk,
            video__video_id=self.kwargs["video_id"],
        )
        return video_rate_later

    def get(self, request, *args, **kwargs):
        """Fetch a video from user's rate later list"""
        verify_username(request, kwargs["username"])
        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Deletes a video from user's rate later list"""
        verify_username(request, kwargs["username"])
        return self.destroy(request, *args, **kwargs)
