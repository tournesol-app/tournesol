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

    __already_visited_node__ = set()

    def get_related_entities(self, entity):
        local_entities = set()

        if entity.comparisons_video_1.exists():
            local_entities.update(
                set(
                    map(lambda x: x.entity_2, entity.comparisons_video_1.filter(
                        poll=self.poll_from_url, user=self.request.user
                    ))
                )
            )
        if entity.comparisons_video_2.exists():
            local_entities.update(
                set(
                    map(lambda x: x.entity_1, entity.comparisons_video_2.filter(
                        poll=self.poll_from_url, user=self.request.user
                    ))
                )
            )

        self.__already_visited_node__.add(entity)

        new_set_to_push = set()
        for element in local_entities:
            if element not in self.__already_visited_node__:
                new_set_to_push.update(self.get_related_entities(element))

        local_entities.update(new_set_to_push)

        return local_entities

    def get_queryset(self):
        # Get related entities from source
        source_node = Entity.objects.none()

        if self.kwargs.get("uid"):
            entity_uid = self.kwargs.get("uid")
            source_node = Entity.objects.get(uid=entity_uid)
        else:
            return Entity.objects.none()

        user_related_entities = self.get_related_entities(source_node)
        user_all_entities = set()

        # Get all comparison for the user
        user_comparisons = Comparison.objects.filter(
            poll=self.poll_from_url, user=self.request.user
        )

        for comparison in user_comparisons.iterator():
            if comparison.entity_1 not in user_all_entities:
                user_all_entities.add(comparison.entity_1)
            if comparison.entity_2 not in user_all_entities:
                user_all_entities.add(comparison.entity_2)

        return Entity.objects \
            .filter(id__in=(entity.id for entity in user_all_entities)) \
            .exclude(id__in=(entity.id for entity in user_related_entities))
