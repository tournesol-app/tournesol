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
from tournesol.serializers.rate_later import RateLaterLegacySerializer, RateLaterSerializer
from tournesol.views.mixins.poll import PollScopedViewMixin


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
class LegacyRateLaterList(generics.ListCreateAPIView):
    """
    List all videos of a user's rate later list, or add a video to the list.
    """

    serializer_class = RateLaterLegacySerializer
    permission_classes = [IsAuthenticated]
    queryset = RateLater.objects.none()

    default_poll: Poll

    def initial(self, request, *args, **kwargs):
        """
        Runs anything that needs to occur prior to calling the method handler.
        """
        super().initial(request, *args, **kwargs)

        # make the requested poll available at any time in the view
        self.default_poll = Poll.default_poll()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["poll"] = self.default_poll
        return context

    def get_queryset(self):
        return RateLater.objects.filter(user=self.request.user).prefetch_related(
            "entity"
        )


@extend_schema_view(
    get=extend_schema(description="Fetch a video from user's rate later list"),
    delete=extend_schema(description="Delete a video from user's rate later list"),
)
class LegacyRateLaterDetail(generics.RetrieveDestroyAPIView):
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
            poll=Poll.default_poll(),
        )
        return rate_later


@extend_schema_view(
    get=extend_schema(
        description="List all entities of the logged user's rate-later list, for a given poll."
    ),
    post=extend_schema(
        description="Add a new entity to the logged user's rate-later list, for a given poll.",
        responses={
            200: RateLaterSerializer,
            409: OpenApiResponse(
                description="The entity is already in the user's rate-later list of this poll,"
                            " or there is an other error with the database query."
            ),
        }
    ),
)
class RateLaterList(PollScopedViewMixin, generics.ListCreateAPIView):
    """
    List all entities of a user's rate-later list in a specific poll, or add a
    new entity to the list.
    """

    permission_classes = [IsAuthenticated]
    queryset = RateLater.objects.none()
    serializer_class = RateLaterSerializer

    def get_queryset(self):
        return RateLater.objects.filter(
            poll=self.poll_from_url, user=self.request.user
        ).prefetch_related("entity")


@extend_schema_view(
    get=extend_schema(
        description="Get an entity from the logged user's rate-later list."
    ),
    delete=extend_schema(
        description="Delete an entity from the logged user's rate-later list."
    ),
)
class RateLaterDetail(PollScopedViewMixin, generics.RetrieveDestroyAPIView):
    """
    Get, or delete an entity from a user's rate-later list in a specific poll.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = RateLaterSerializer

    def get_object(self):
        rate_later = get_object_or_404(
            RateLater,
            poll=self.poll_from_url,
            user=self.request.user,
            entity__uid=self.kwargs.get("uid"),
        )

        return rate_later
