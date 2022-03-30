"""
API endpoints to show unconnected entities
"""
from collections import defaultdict

from django.db.models import ObjectDoesNotExist
from django.http import Http404
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

    __already_visited_node__ = set()
    __all_entites__ = set()
    __all_connections__ = defaultdict(set)

    def get_related_entities(self, entity_id):

        self.__already_visited_node__.add(entity_id)
        self.__all_entites__.remove(entity_id)

        related_entities = set()
        for other_node in self.__all_connections__.get(entity_id):
            if other_node not in self.__already_visited_node__:
                related_entities.update(self.get_related_entities(other_node))

        return self.__all_connections__.get(entity_id).union(related_entities)

    def get_queryset(self):
        # Get related entities from source
        source_node = Entity.objects.none()

        try:
            entity_uid = self.kwargs.get("uid")
            source_node = Entity.objects.get(uid=entity_uid)
        except ObjectDoesNotExist:
            raise Http404

        comparisons = list(Comparison.objects.filter(
            poll=self.poll_from_url, user=self.request.user
        ))

        self.__all_entites__ = set(c.entity_1_id for c in comparisons).union(
            set(c.entity_2_id for c in comparisons))
        for c in comparisons:
            self.__all_connections__[c.entity_1_id].add(c.entity_2_id)
            self.__all_connections__[c.entity_2_id].add(c.entity_1_id)

        user_related_entities = self.get_related_entities(source_node.id)
        user_all_entities = set()

        # Get all comparison for the user
        user_comparisons = Comparison.objects.filter(
            poll=self.poll_from_url, user=self.request.user
        )

        for comparison in user_comparisons.iterator():
            user_all_entities.add(comparison.entity_1)
            user_all_entities.add(comparison.entity_2)

        return Entity.objects \
            .filter(id__in=(entity.id for entity in user_all_entities)) \
            .exclude(id__in=(entity_id for entity_id in user_related_entities))
