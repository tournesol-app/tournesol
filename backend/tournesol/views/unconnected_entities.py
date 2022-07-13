"""
API endpoints interacting with unconnected entities.
"""
from collections import defaultdict

from django.db.models import Func, OuterRef, Q, Subquery
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.models import Comparison, Entity
from tournesol.serializers.entity import EntityNoExtraFieldSerializer
from tournesol.views.mixins.poll import PollScopedViewMixin


@extend_schema_view(
    get=extend_schema(
        description="List unconnected entities of the current user from a target entity"
                    " and the user's graph of comparisons (entities are vertices and"
                    " comparisons are edges)."
    )
)
class UnconnectedEntitiesView(PollScopedViewMixin, generics.ListAPIView):
    """
    List unconnected entities.
    """

    serializer_class = EntityNoExtraFieldSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get related entities from source entity
        source_node = get_object_or_404(Entity, uid=self.kwargs.get("uid"))
        comparisons = list(
            Comparison.objects.filter(
                poll=self.poll_from_url, user=self.request.user
            ).values_list("entity_1_id", "entity_2_id")
        )

        all_connections = defaultdict(set)

        for (entity_1_id, entity_2_id) in comparisons:
            all_connections[entity_1_id].add(entity_2_id)
            all_connections[entity_2_id].add(entity_1_id)

        def get_related_entities(entity_id):
            already_visited_nodes = set()
            related_entities = {entity_id}
            to_visit = {entity_id}

            while to_visit:
                node = to_visit.pop()
                already_visited_nodes.add(node)
                connections = all_connections.get(node, set())
                to_visit.update(connections - already_visited_nodes)
                related_entities.update(connections)

            return related_entities

        user_related_entities = get_related_entities(source_node.id)
        user_all_entities = set()

        for (entity_1_id, entity_2_id) in comparisons:
            user_all_entities.add(entity_1_id)
            user_all_entities.add(entity_2_id)

        # Order the entities by number of comparisons so that the logged user
        # is invited to compare entities with the least comparisons first.
        comparison_counts = (
            Comparison.objects.filter(user=self.request.user)
            .filter(Q(entity_1=OuterRef("pk")) | Q(entity_2=OuterRef("pk")))
            .annotate(count=Func("id", function="Count"))
            .values("count")
        )

        return (
            Entity.objects.filter(id__in=user_all_entities - user_related_entities)
            .annotate(n_comparisons=Subquery(comparison_counts))
            .order_by("n_comparisons")
        )
