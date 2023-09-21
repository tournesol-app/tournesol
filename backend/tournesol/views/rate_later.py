"""
API endpoint to manipulate contributor's rate later list
"""

from django.db.models import Prefetch, prefetch_related_objects
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.models import Entity, RateLater
from tournesol.serializers.rate_later import RateLaterSerializer
from tournesol.views.mixins.poll import PollScopedViewMixin


class RateLaterQuerysetMixin(PollScopedViewMixin):
    def get_prefetch_entity_config(self):
        poll = self.poll_from_url
        return Prefetch(
            "entity",
            queryset=(
                Entity.objects.with_prefetched_poll_ratings(
                    poll_name=poll.name
                ).with_prefetched_contributor_ratings(poll=poll, user=self.request.user)
            ),
        )

    def get_queryset(self):
        poll = self.poll_from_url
        return RateLater.objects.filter(poll=poll, user=self.request.user).prefetch_related(
            self.get_prefetch_entity_config()
        )

    def prefetch_entity(self, rate_later: RateLater):
        prefetch_related_objects([rate_later], self.get_prefetch_entity_config())


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
class RateLaterList(RateLaterQuerysetMixin, generics.ListCreateAPIView):
    """
    List all entities of a user's rate-later list in a specific poll, or add a
    new entity to the list.
    """

    permission_classes = [IsAuthenticated]
    queryset = RateLater.objects.none()
    serializer_class = RateLaterSerializer

    def perform_create(self, serializer):
        rate_later = serializer.save()
        self.prefetch_entity(rate_later)


@extend_schema_view(
    get=extend_schema(description="Get an entity from the logged user's rate-later list."),
    delete=extend_schema(description="Delete an entity from the logged user's rate-later list."),
)
class RateLaterDetail(RateLaterQuerysetMixin, generics.RetrieveDestroyAPIView):
    """
    Get, or delete an entity from a user's rate-later list in a specific poll.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = RateLaterSerializer

    lookup_field = "entity__uid"
    lookup_url_kwarg = "uid"
