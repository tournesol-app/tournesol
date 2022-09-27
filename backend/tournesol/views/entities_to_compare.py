from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from tournesol.models import Entity
from tournesol.models.poll import DEFAULT_POLL_NAME
from tournesol.serializers.entity import EntityNoExtraFieldSerializer
from tournesol.suggestions.suggester_store import SuggesterStore
from tournesol.views import PollScopedViewMixin


@extend_schema_view(
    get=extend_schema(
        description="Retrieve suggested entities to compare for the logged user",
        parameters=[
            OpenApiParameter(
                "first_entity_uid", OpenApiTypes.STR, OpenApiParameter.QUERY
            )
        ],
    )
)
class EntitiesToCompareView(PollScopedViewMixin, ListAPIView):
    """
    Return suggestions of entities to compare for the logged user.
    """
    serializer_class = EntityNoExtraFieldSerializer

    def list(self, request, *args, **kwargs):
        poll = self.poll_from_url
        if poll.name != DEFAULT_POLL_NAME:
            raise ValidationError({"detail": "only poll 'videos' is supported"})

        user = self.request.user
        suggester = SuggesterStore.actual_store.get_suggester(poll)

        opt_first_entity = self.request.query_params.get("first_entity_uid")
        limit = int(self.request.query_params.get("limit", 10))
        if opt_first_entity is None:
            suggestions = suggester.get_first_video_recommendation(user, limit)
        else:
            suggestions = suggester.get_second_video_recommendation(user, opt_first_entity, limit)

        entities = {
            e.uid: e
            for e in Entity.objects.filter(
                uid__in=(s.uid for s in suggestions)
            )
        }
        ser = self.get_serializer([entities[s.uid] for s in suggestions], many=True)
        return Response({"results": ser.data})
