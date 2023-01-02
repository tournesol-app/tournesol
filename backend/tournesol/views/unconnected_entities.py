"""
API endpoints interacting with unconnected entities.
"""
from collections import defaultdict, deque

from django.db.models import Case, Func, OuterRef, Q, Subquery, When
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.models import Comparison, Entity
from tournesol.serializers.entity import EntityNoExtraFieldSerializer
from tournesol.views.mixins.poll import PollScopedViewMixin


@extend_schema_view(
    get=extend_schema(
        description="List unconnected entities of the current user from a target entity"
                    " and the user's graph of comparisons (entities are vertices and"
                    " comparisons are edges).",
        parameters=[
            OpenApiParameter(
                "strict",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description=(
                    "Set to 'false' to include entities connected to the target entity. In this "
                    "case, the returned list contains first all unconnected entities, then "
                    "connected entities sorted by decreasing distance to the target entity."
                ),
                required=False,
            )
        ]
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

        neighbors = defaultdict(set)
        for (entity_1_id, entity_2_id) in Comparison.objects.filter(
            poll=self.poll_from_url, user=self.request.user
        ).values_list("entity_1_id", "entity_2_id"):
            neighbors[entity_1_id].add(entity_2_id)
            neighbors[entity_2_id].add(entity_1_id)

        distances = {source_node.id: 0}
        bfs_queue = deque([(source_node.id, 0)])

        while bfs_queue:
            node, distance = bfs_queue.popleft()
            for next_node in neighbors[node]:
                if next_node not in distances:
                    distances[next_node] = distance+1
                    bfs_queue.append((next_node, distance+1))

        # The entities filtered are the entities which don't have a distance
        # because they are unreachable if the strict option has been left to
        # True (the default). Otherwise all the entities except the source are
        # selected.
        strict = self.request.GET.get("strict") != "false"
        entity_ids_filter = set(neighbors) - (set(distances) if strict else {source_node.id})

        # From the computed distances, creates the cases for annotating and
        # ordering the returned list of entities.
        distance_annotation_whens = [
            When(id=k, then=distances[k]) for k in entity_ids_filter if k in distances
        ]

        # Order the entities by number of comparisons so that the logged user
        # is invited to compare entities with the least comparisons first.
        comparison_counts = (
            Comparison.objects.filter(user=self.request.user)
            .filter(Q(entity_1=OuterRef("pk")) | Q(entity_2=OuterRef("pk")))
            .annotate(count=Func("id", function="Count"))
            .values("count")
        )

        return (
            Entity.objects.filter(id__in=entity_ids_filter)
            .annotate(distance=Case(*distance_annotation_whens, default=1+len(neighbors)))
            .annotate(n_comparisons=Subquery(comparison_counts))
            .order_by("-distance", "n_comparisons")
        )
