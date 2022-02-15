from django.db.models import Prefetch
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.viewsets import ReadOnlyModelViewSet

from tournesol.entities import ENTITY_TYPE_CHOICES
from tournesol.models import Entity, EntityCriteriaScore
from tournesol.serializers.entity import EntitySerializer

filter_parameters = [
    OpenApiParameter(
        "type",
        description="Type of entities to return",
        enum=map(lambda x: x[0], ENTITY_TYPE_CHOICES),
    ),
    OpenApiParameter(
        "poll_name",
        description="If defined, only scores related to this poll will be returned",
    ),
]


@extend_schema_view(
    list=extend_schema(parameters=filter_parameters),
    retrieve=extend_schema(parameters=filter_parameters),
)
class EntitiesViewSet(ReadOnlyModelViewSet):
    """
    Fetch entities and their detailed scores in all polls
    """

    permission_classes = []
    queryset = Entity.objects.none()
    lookup_field = "uid"
    serializer_class = EntitySerializer

    def get_queryset(self):
        request = self.request
        queryset = Entity.objects.all()

        entity_type = request.query_params.get("type")
        if entity_type:
            queryset = queryset.filter(type=entity_type)

        poll_name = request.query_params.get("poll_name")
        if poll_name:
            criteria_scores_queryset = EntityCriteriaScore.objects.filter(
                poll__name=poll_name
            )
        else:
            criteria_scores_queryset = EntityCriteriaScore.objects.all()

        return queryset.prefetch_related(
            Prefetch(
                "criteria_scores",
                queryset=criteria_scores_queryset.select_related("poll"),
            )
        )
