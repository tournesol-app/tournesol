from django.db import models
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.serializers.suggestion import ResultFromPollRating
from tournesol.views import PollScopedViewMixin

from .strategies.classic import ClassicEntitySuggestionStrategy


class ToCompareStrategy(models.TextChoices):
    CLASSIC = "CLASSIC"


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                name="strategy",
                required=False,
                enum=ToCompareStrategy.values,
                default=ToCompareStrategy.CLASSIC,
                description="The strategy used to suggest a entities to compare.",
            ),
        ],
    )
)
class SuggestionsToCompare(PollScopedViewMixin, generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ResultFromPollRating

    strategy = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        strategy = request.query_params.get("strategy", ToCompareStrategy.CLASSIC)

        if strategy == ToCompareStrategy.CLASSIC:
            self.strategy = ClassicEntitySuggestionStrategy(request, self.poll_from_url)
        else:
            # Fallback to the classic strategy if an unknown strategy is provided.
            self.strategy = ClassicEntitySuggestionStrategy(request, self.poll_from_url)

    def get_serializer_class(self):
        return self.strategy.get_serializer_class()

    def get_queryset(self):
        return self.strategy.get_results()
