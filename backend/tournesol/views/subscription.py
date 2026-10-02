"""
API endpoints to manage the logged user's subscriptions to entity sources.
"""

from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.models.subscription import Subscription
from tournesol.serializers.subscription import SubscriptionSerializer
from tournesol.throttling import (
    BurstAnonRateThrottle,
    BurstUserRateThrottle,
    PostScopeRateThrottle,
    SustainedAnonRateThrottle,
    SustainedUserRateThrottle,
)


class SubscriptionQuerysetMixin:
    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user).select_related(
            "entity_source"
        )


@extend_schema_view(
    get=extend_schema(description="List all the logged user's subscriptions."),
    post=extend_schema(
        description="Subscribe the logged user to a new source.",
        responses={
            201: SubscriptionSerializer,
            400: OpenApiResponse(
                description="The source does not exist, or the uid is malformed."
            ),
            409: OpenApiResponse(
                description="The user is already subscribed to this source."
            ),
        },
    ),
)
class SubscriptionList(SubscriptionQuerysetMixin, generics.ListCreateAPIView):
    """List the logged user's subscriptions, or subscribe to a new source."""

    permission_classes = [IsAuthenticated]
    queryset = Subscription.objects.none()
    serializer_class = SubscriptionSerializer

    throttle_classes = [
        PostScopeRateThrottle,
        BurstAnonRateThrottle,
        BurstUserRateThrottle,
        SustainedAnonRateThrottle,
        SustainedUserRateThrottle,
    ]

    throttle_scope = "api_subscription_post"


@extend_schema_view(
    get=extend_schema(description="Retrieve one of the logged user's subscriptions."),
    delete=extend_schema(description="Unsubscribe the logged user from a source."),
)
class SubscriptionDetail(SubscriptionQuerysetMixin, generics.RetrieveDestroyAPIView):
    """Retrieve or delete one of the logged user's subscriptions."""

    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializer
    lookup_field = "entity_source__uid"
    lookup_url_kwarg = "source_uid"
