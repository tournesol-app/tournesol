"""
API endpoint to maniuplate contributor's rate later list
"""

from django.db import IntegrityError
from django.shortcuts import get_object_or_404
from rest_framework import generics, mixins, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from tournesol.models import Video, VideoRateLater
from tournesol.serializers import VideoRateLaterSerializer


class VideoRateLaterList(
    mixins.ListModelMixin, mixins.CreateModelMixin, generics.GenericAPIView
):
    """
    List all videos of a user's rate later list, or add a video to the list.
    """

    serializer_class = VideoRateLaterSerializer

    def get_queryset(self):
        return VideoRateLater.objects.filter(user__pk=self.kwargs["user_id"])

    def get(self, request, *args, **kwargs):
        """API call to return list of rate_later videos"""
        if request.user.pk != self.kwargs["user_id"]:
            raise PermissionDenied("403 Forbidden")

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
        if request.user.pk != self.kwargs["user_id"]:
            raise PermissionDenied("403 Forbidden")

        try:
            video = get_object_or_404(Video, video_id=request.data["video.video_id"])
        except KeyError:
            return Response(
                {
                    "detail": "Required field video.video_id not fount.",
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
        if request.user.pk != self.kwargs["user_id"]:
            raise PermissionDenied("403 Forbidden")

        return self.retrieve(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        """Deletes a video from user's rate later list"""
        if request.user.pk != self.kwargs["user_id"]:
            raise PermissionDenied("403 Forbidden")

        return self.destroy(request, *args, **kwargs)
