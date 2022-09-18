"""
API endpoint to manipulate contributor's rate later list
"""

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.models import RateLater
from tournesol.serializers.rate_later import RateLaterSerializer
from tournesol.views.mixins.poll import PollScopedViewMixin


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
        },
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
