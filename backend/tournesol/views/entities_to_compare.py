from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from tournesol.suggestions.suggester import Suggester
from tournesol.models import Poll
from tournesol.serializers.entity import EntityNoExtraFieldSerializer
from tournesol.views import PollScopedViewMixin


@extend_schema_view(
    get=extend_schema(
        description="Retrieve a list of recommendations for the logged user to compare",
        parameters=[
            OpenApiParameter(
                "first_entity_uid", OpenApiTypes.STR, OpenApiParameter.QUERY
            )
        ],
    )
)
class EntitiesToCompareView(PollScopedViewMixin, ListAPIView):
    serializer_class = EntityNoExtraFieldSerializer
    recommender: dict[Poll, Suggester] = {}

    # Singleton
    @classmethod
    def get_ready(cls, poll: Poll):
        cls.recommender[poll] = Suggester()

    def list(self, request, **kwargs):
        poll = self.poll_from_url
        if poll not in self.recommender.keys():
            EntitiesToCompareView.get_ready(poll)
        user = self.request.user

        opt_first_entity = self.request.query_params.get("first_entity_uid")
        limit = int(self.request.query_params.get("limit", 10))
        if opt_first_entity is None:
            entities = self.recommender[poll].get_first_video_recommendation(user, limit)
        else:
            entities = self.recommender[poll].get_second_video_recommendation(
                user, opt_first_entity, limit
            )

        ser = self.get_serializer(entities, many=True)
        return Response(ser.data)
