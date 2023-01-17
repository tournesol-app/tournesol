from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

import logging
import time

from tournesol.models import Entity
from tournesol.models.poll import DEFAULT_POLL_NAME
from tournesol.serializers.entity import EntityNoExtraFieldSerializer
from tournesol.suggestions.suggester_store import SuggesterStore
from tournesol.views import PollScopedViewMixin


logger = logging.getLogger(__name__)

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
        begin = time.perf_counter()
        poll = self.poll_from_url


        if poll.name != DEFAULT_POLL_NAME:
            raise ValidationError({"detail": "only poll 'videos' is supported"})

        user = self.request.user
        suggester = SuggesterStore.actual_store.get_suggester(poll)
        logger.debug("Built SuggesterStore: %.3fs" % (time.perf_counter() - begin))

        opt_first_entity = self.request.query_params.get("first_entity_uid")
        limit = int(self.request.query_params.get("limit", 10))
        if opt_first_entity is None:
            begin = time.perf_counter()
            logger.debug("Start getting first video")
            suggestions = suggester.get_first_video_recommendation(user, limit)
            logger.debug("Got first video: %.3fs" % (time.perf_counter() - begin))

        else:
            suggestions = suggester.get_second_video_recommendation(user, opt_first_entity, limit)


        sorted_entity_ids = [s.uid for s in suggestions]
        entities = {e.uid: e for e in Entity.objects.filter(uid__in=sorted_entity_ids)}
        ser = self.get_serializer([entities[e_id] for e_id in sorted_entity_ids], many=True)
        return Response({"results": ser.data})
