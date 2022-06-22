"""
API endpoint to manipulate contributor's rate later list
"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.models import Entity, Poll, RateLater
from tournesol.serializers.rate_later import RateLaterSerializer


class VideosScopedViewMixin():
    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)

        # make the default poll
        self.poll_from_url = Poll.default_poll()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["poll"] = Poll.default_poll()
        return context


@extend_schema_view(
    post=extend_schema(
        responses={
            200: RateLaterSerializer,
            409: OpenApiResponse(
                description="Conflict: the video is already in the rate later list,"
                " or there is an other error with the database query."
            ),
        }
    )
)
class RateLaterList(VideosScopedViewMixin, generics.ListCreateAPIView):
    """
    List all videos of a user's rate later list, or add a video to the list.
    """

    serializer_class = RateLaterSerializer
    permission_classes = [IsAuthenticated]
    queryset = RateLater.objects.none()

    def get_queryset(self):
        return RateLater.objects.filter(user=self.request.user, poll=Poll.default_poll())


@extend_schema_view(
    get=extend_schema(description="Fetch a video from user's rate later list"),
    delete=extend_schema(description="Delete a video from user's rate later list"),
)
class RateLaterDetail(VideosScopedViewMixin, generics.RetrieveDestroyAPIView):
    """
    Retrieve, or delete a video from a user's rate later list.
    """

    serializer_class = RateLaterSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """Fetch a given video or returns 404"""

        rate_later = get_object_or_404(
            RateLater,
            user__pk=self.request.user.pk,
            entity=Entity.get_from_video_id(self.kwargs["uid"]),
            poll=Poll.default_poll(),
        )
        return rate_later
