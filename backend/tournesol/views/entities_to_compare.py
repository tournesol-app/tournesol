from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from recommendation.recommender import Recommender
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
    recommender: Recommender = None

    # Singleton
    @classmethod
    def get_ready(cls):
        cls.recommender = Recommender()

    def list(self, request, **kwargs):
        # poll = self.poll_from_url
        user = self.request.user

        opt_first_entity = self.request.query_params.get("first_entity_uid")
        limit = int(self.request.query_params.get("limit", 10))
        if opt_first_entity is None:
            entities = self.recommender.get_first_video_recommendation(user, limit)
        else:
            entities = self.recommender.get_second_video_recommendation(
                user, opt_first_entity, limit
            )

        ser = self.get_serializer(entities, many=True)
        return Response(ser.data)
