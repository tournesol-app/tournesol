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

    def get_queryset(self):
        # Get related entities from source entity
        source_node = get_object_or_404(Entity, uid=self.kwargs.get("uid"))
        comparison_pairs = list(
            Comparison.objects.filter(
                poll=self.poll_from_url, user=self.request.user
            ).values_list("entity_1_id", "entity_2_id")
        )

        all_connections = defaultdict(set)
        already_visited_nodes = set()

        for (entity_1_id, entity_2_id) in comparison_pairs:
            all_connections[entity_1_id].add(entity_2_id)
            all_connections[entity_2_id].add(entity_1_id)

        def get_related_entities(entity_id):
            already_visited_nodes.add(entity_id)
            related_entities = set()
            if entity_id not in all_connections:
                return set()

            for other_node in all_connections[entity_id]:
                if other_node not in already_visited_nodes:
                    related_entities.update(get_related_entities(other_node))

            return all_connections[entity_id].union(related_entities)

        user_related_entities = get_related_entities(source_node.id)
        user_all_entities = set()

        for (entity_1_id, entity_2_id) in comparison_pairs:
            user_all_entities.add(entity_1_id)
            user_all_entities.add(entity_2_id)

        return Entity.objects.filter(id__in=user_all_entities - user_related_entities)
