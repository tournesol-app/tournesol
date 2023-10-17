from enum import Enum

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.serializers.suggestion import ResultFromRelatedEntity
from tournesol.views import PollScopedViewMixin

from .strategies.classic import ClassicEntitySuggestionStrategy


class ToCompareStrategy(Enum):
    CLASSIC = 0


class EntityToCompare(PollScopedViewMixin, generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultFromRelatedEntity

    strategy = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        # TODO: select the strategy from the request's parameters
        self.strategy = ClassicEntitySuggestionStrategy(request, self.poll_from_url)

    def get_serializer_class(self):
        return self.strategy.get_serializer_class()

    def get_object(self):
        return self.strategy.get_result()
