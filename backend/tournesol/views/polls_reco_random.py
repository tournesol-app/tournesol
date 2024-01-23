from django.utils.decorators import method_decorator
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)

from tournesol.models import Entity
from tournesol.serializers.poll import (
    RecommendationBaseSerializer,
    RecommendationsRandomFilterSerializer,
)
from tournesol.utils.cache import cache_page_no_i18n
from tournesol.views import PollRecommendationsBaseAPIView


class RandomRecommendationBaseAPIView(PollRecommendationsBaseAPIView):
    query_params_serializer = RecommendationsRandomFilterSerializer

    def get_queryset(self):
        """
        Return a queryset of random recommended entities.

        This queryset is designed to be more performant than the queryset
        of the regular recommendations view. For this reason, it doesn't allow
        to:
            - filter entities by text
            - filter entities by weighted criteria score
            - or anything involving a SQL JOIN on EntityCriteriaScore
        """
        poll = self.poll_from_url
        queryset = Entity.objects.all()
        queryset, _ = self.filter_by_parameters(self.request, queryset, poll)
        queryset = queryset.with_prefetched_scores(poll_name=poll.name)
        queryset = queryset.with_prefetched_poll_ratings(poll_name=poll.name)
        queryset = queryset.filter_safe_for_poll(poll)
        queryset = queryset.order_by("?")
        return queryset


@extend_schema_view(
    get=extend_schema(
        parameters=[
            RecommendationsRandomFilterSerializer,
            OpenApiParameter(
                "metadata",
                OpenApiTypes.OBJECT,
                style="deepObject",
                description="Filter by one or more metadata.",
                examples=[
                    OpenApiExample(
                        name="No metadata filter",
                    ),
                    OpenApiExample(
                        name="Videos - some examples",
                        value={"language": ["en", "pt"], "uploader": "Kurzgesagt – In a Nutshell"},
                    ),
                    OpenApiExample(
                        name="Videos - videos of 8 minutes or less (480 sec)",
                        value={"duration:lte:int": "480"},
                    ),
                    OpenApiExample(
                        name="Candidates - some examples",
                        value={
                            "name": "A candidate full name",
                            "youtube_channel_id": "channel ID",
                        },
                    ),
                ],
            ),
        ],
    )
)
class RandomRecommendationList(RandomRecommendationBaseAPIView):
    """
    Return a random list of recommended entities.
    """

    permission_classes = []
    serializer_class = RecommendationBaseSerializer
    poll_parameter = "name"

    @method_decorator(cache_page_no_i18n(60 * 10))
    def get(self, request, *args, **kwargs):
        return self.list(self, request, *args, **kwargs)
