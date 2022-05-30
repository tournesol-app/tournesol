"""
API endpoints to show unconnected entities
"""
from collections import defaultdict

from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.views.mixins.poll import PollScopedViewMixin

from ..models import Comparison, Entity
from ..serializers.entity import EntityNoExtraFieldSerializer


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
    serializer_class = EntityNoExtraFieldSerializer
    permission_classes = [IsAuthenticated]

    _already_visited_node_ = set()
    _all_connections_ = defaultdict(set)

    def get_related_entities(self, entity_id):

        self._already_visited_node_.add(entity_id)

        related_entities = set()
        if self._all_connections_.get(entity_id) is None:
            return set()

        for other_node in self._all_connections_.get(entity_id):
            if other_node not in self._already_visited_node_:
                related_entities.update(self.get_related_entities(other_node))

        return self._all_connections_.get(entity_id).union(related_entities)

    def get_queryset(self):
        # Get related entities from source
        source_node = Entity.objects.none()

        source_node = get_object_or_404(Entity, uid=self.kwargs.get("uid"))
        comparisons = list(Comparison.objects.filter(
            poll=self.poll_from_url, user=self.request.user
        ))

        for c in comparisons:
            self._all_connections_[c.entity_1_id].add(c.entity_2_id)
            self._all_connections_[c.entity_2_id].add(c.entity_1_id)

        user_related_entities = self.get_related_entities(source_node.id)
        user_all_entities = set()

        for comparison in comparisons:
            user_all_entities.add(comparison.entity_1_id)
            user_all_entities.add(comparison.entity_2_id)

        return Entity.objects \
            .filter(id__in=user_all_entities - user_related_entities)
