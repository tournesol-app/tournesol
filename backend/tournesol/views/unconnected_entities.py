"""
API endpoints interacting with unconnected entities.
"""
import math
from collections import defaultdict, deque

from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated

from tournesol.models import Comparison, Entity
from tournesol.serializers.unconnected_entities import UnconnectedEntitySerializer
from tournesol.views.mixins.poll import PollScopedViewMixin


# We override the pagination filtering for our queryset for performance reasons. We decided to
# already filter and sort the queryset in python directly because the annotation and sorting
# operations were inneficient when done on the database.
class SortedEntityIdLimitOffsetPagination(LimitOffsetPagination):

    def paginate_queryset(self, queryset, request, view=None):
        # Here the parameter queryset is instead the list of ids returned by
        # UnconnectedEntitiesView.get_queryset. This is done this way for performance.
        paginated_entity_ids = super().paginate_queryset(queryset, request, view)
        entity_by_id = {e.id: e for e in Entity.objects.filter(id__in=paginated_entity_ids)}
        entities = [entity_by_id[e_id] for e_id in queryset if e_id in entity_by_id]
        return entities


@extend_schema_view(
    get=extend_schema(
        description="List unconnected entities of the current user from a target entity"
                    " and the user's graph of comparisons (entities are vertices and"
                    " comparisons are edges).",
        parameters=[
            OpenApiParameter(
                "strict",
                type=OpenApiTypes.BOOL,
                default=True,
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

    serializer_class = UnconnectedEntitySerializer
    permission_classes = [IsAuthenticated]
    pagination_class = SortedEntityIdLimitOffsetPagination

    enable_entity_contexts = True

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
        strict = self.request.query_params.get("strict") != "false"
        entity_ids = set(e_id for e_id in neighbors if (
            (e_id not in distances) if strict else (distances.get(e_id, 2) > 1)
        ))
        sorted_entity_ids = sorted(
            entity_ids,
            # Sorting first by distance and secondly by number of comparisons
            # and thirdly by entity_id such that we avoid non-determinism
            key=lambda x: (-distances.get(x, math.inf), len(neighbors.get(x, [])), x)
        )
        return sorted_entity_ids
