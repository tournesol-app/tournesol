from django.db import models
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from tournesol.lib.suggestions.strategies import ClassicEntitySuggestionStrategy
from tournesol.serializers.suggestion import EntityToCompare
from tournesol.views import PollScopedViewMixin


class ToCompareStrategy(models.TextChoices):
    CLASSIC = "classic"


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
    """
    Suggest a list of entities to compare to the logged-in user.

    The suggestion strategy is determined by the `strategy` query parameter.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = EntityToCompare

    strategy = None

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        strategy = request.query_params.get("strategy", ToCompareStrategy.CLASSIC)

        if strategy == ToCompareStrategy.CLASSIC:
            self.strategy = ClassicEntitySuggestionStrategy(self.poll_from_url, request.user)
        else:
            # Fallback to the classic strategy if an unknown strategy is provided.
            self.strategy = ClassicEntitySuggestionStrategy(self.poll_from_url, request.user)

    def get_queryset(self):
        return self.strategy.get_results()
