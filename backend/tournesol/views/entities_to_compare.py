from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from recommendation.recommender import Recommender
from tournesol.serializers.entity import EntityNoExtraFieldSerializer
from tournesol.views import PollScopedViewMixin


class EntitiesToCompareView(PollScopedViewMixin, ListAPIView):
    serializer_class = EntityNoExtraFieldSerializer
    recommender: Recommender = None

    # Singleton
    def get_ready(self):
        self.recommender = Recommender()

    def list(self, request, **kwargs):
        poll = self.poll_from_url
        user = self.request.user

        opt_first_entity = self.request.query_params.get("first_entity_uid")
        limit = self.request.query_params.get("limit", 10)
        if opt_first_entity is None:
            entities = self.recommender.get_first_video_recommendation(user, limit)
        else:
            entities = self.recommender.get_second_video_recommendation(user, first_video_id=opt_first_entity,
                                                                        nb_video_required=limit)

        ser = self.get_serializer(entities, many=True)
        return Response(ser.data)
