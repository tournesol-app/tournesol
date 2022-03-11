"""
API endpoints to show unconnected entities
"""
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.views.mixins.poll import PollScopedViewMixin

from ..models import Comparison, Entity
from ..serializers.entity import EntitySerializer


@extend_schema_view(
    get=extend_schema(description="Show unconnected entities for the current user")
)
class UnconnectedEntitiesView(
    PollScopedViewMixin,
    generics.ListAPIView
):
    """
    API view for showing unconnected entities
    """
    serializer_class = EntitySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the main entities
        user_comparaisons = Comparison.objects.filter(
            poll=self.poll_from_url, user=self.request.user
        )

        connected_entities_uid_list = []
        unconnected_entities_uid_list = []

        if self.kwargs.get("id"):
            # Add search value in the list
            connected_entities_uid_list.append(self.kwargs.get("id"))

        # Diclaimer : This implementation doesn't work.
        # It doesn't take non direct link into account
        for comparison in user_comparaisons.iterator():
            if (
                comparison.entity_1.id in connected_entities_uid_list and
                comparison.entity_2.id not in connected_entities_uid_list
            ):
                connected_entities_uid_list.append(comparison.entity_2.id)
            if (
                comparison.entity_2.id in connected_entities_uid_list and
                comparison.entity_1.id not in connected_entities_uid_list
            ):
                connected_entities_uid_list.append(comparison.entity_1.id)
            if (
                comparison.entity_1.id not in connected_entities_uid_list and
                comparison.entity_2.id not in connected_entities_uid_list
            ):
                unconnected_entities_uid_list.append(comparison.entity_1.id)
                unconnected_entities_uid_list.append(comparison.entity_2.id)

        entities_query_set = Entity.objects.filter(id__in=unconnected_entities_uid_list)

        return entities_query_set
