"""
API endpoint to manipulate contributor's rate later list
"""

from django.db.models import Prefetch, prefetch_related_objects
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.models import Entity, RateLater
from tournesol.models.ratings import ContributorRating
from tournesol.serializers.rate_later import RateLaterSerializer
from tournesol.utils.constants import RATE_LATER_BULK_MAX_SIZE
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
    post=extend_schema(
        description="Add a multiple new entities to the logged user's rate-later list,"
        " for a given poll.",
        request=RateLaterSerializer(many=True),
        responses={
            201: RateLaterSerializer(many=True),
        },
    ),
)
class RateLaterBulkCreate(RateLaterQuerysetMixin, generics.CreateAPIView):
    """
    Create multiple rate-later entries at once.
    Accepts an array of entities to be added to the rate-later list.
    """

    pagination_class = None
    permission_classes = [IsAuthenticated]
    throttle_scope = "api_rate_later_bulk_create"
    serializer_class = RateLaterSerializer

    def get_serializer(self, *args, **kwargs):
        kwargs["many"] = True
        kwargs["max_length"] = RATE_LATER_BULK_MAX_SIZE
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        rate_later_instances = serializer.save()

        if self.request.query_params.get("entity_seen", "false") == "true":
            for rate_later in serializer.validated_data:
                ContributorRating.objects.update_or_create(
                    poll_id=self.poll_from_url.id,
                    user_id=self.request.user.id,
                    entity_id=rate_later["entity"]["pk"],
                    defaults={"entity_seen": True, "is_public": True},  # XXX: do not set is_public to True during update
                )

        # TOFIX: rate_later_instances seems to always be an empty list
        for rate_later in rate_later_instances:
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
