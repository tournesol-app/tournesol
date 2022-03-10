"""
API endpoints to show unconnected entities
"""
from django.db.models import  Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from ..serializers.entity import EntitySerializer
from ..models import Entity, Comparison


@extend_schema_view(get=extend_schema(description="Show unconnected entities for the current user"))
class UnconnectedEntitiesView(generics.ListCreateAPIView):
    """
    API view for showing unconnected entities
    """
    serializer_class = EntitySerializer
    permission_classes = [IsAuthenticated]
        

    def get(self):
        # Get the main entities
        user_comparaisons = Comparison.objects.filter(
            poll=self.poll_from_url, user=self.request.user
        )

        connected_entities_uid_list = []
        unconnected_entities_uid_list = []

        if self.kwargs.get("uid"):
            # Add search value in the list
            connected_entities_uid_list.append(self.kwargs.get("uid"))

        # Diclaimer : This implementation doesn't work. It doesn't take non direct link into account
        for comparison in user_comparaisons:
            if comparison["entity_1__uid"] in connected_entities_uid_list and comparison["entity_2__uid"] not in connected_entities_uid_list:
                connected_entities_uid_list.append(comparison["entity_2__uid"])
            if comparison["entity_2__uid"] in connected_entities_uid_list and comparison["entity_1__uid"] not in connected_entities_uid_list:
                connected_entities_uid_list.append(comparison["entity_1__uid"])
            if comparison["entity_1__uid"] not in connected_entities_uid_list and comparison["entity_2__uid"] not in connected_entities_uid_list:
                unconnected_entities_uid_list.append(comparison["entity_1__uid"])
                unconnected_entities_uid_list.append(comparison["entity_2__uid"])


        videos_query_set = Entity.objects.filter(id__in=unconnected_entities_uid_list);

        return videos_query_set
