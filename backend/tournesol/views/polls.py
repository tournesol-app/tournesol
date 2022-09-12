import logging

from django.conf import settings
from django.db.models import Case, F, Sum, When
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiExample,
    OpenApiParameter,
    extend_schema,
    extend_schema_view,
)
from rest_framework import serializers
from rest_framework.generics import ListAPIView, RetrieveAPIView

from tournesol.models import Entity, Poll
from tournesol.models.entity_score import ScoreMode
from tournesol.models.poll import ALGORITHM_MEHESTAN
from tournesol.serializers.entity import EntityCriteriaDistributionSerializer
from tournesol.serializers.poll import (
    PollSerializer,
    RecommendationSerializer,
    RecommendationsFilterSerializer,
)
from tournesol.utils.constants import CRITERIA_DEFAULT_WEIGHT, MEHESTAN_MAX_SCALED_SCORE
from tournesol.views import PollScopedViewMixin

logger = logging.getLogger(__name__)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            RecommendationsFilterSerializer,
            OpenApiParameter(
                "weights",
                OpenApiTypes.OBJECT,
                style="deepObject",
                description="Weights for criteria in this poll."
                f" The default weight is {CRITERIA_DEFAULT_WEIGHT} for each criteria.",
                examples=[
                    OpenApiExample(
                        name="Default weights",
                    ),
                    OpenApiExample(
                        name="Weights example",
                        value={
                            "reliability": CRITERIA_DEFAULT_WEIGHT,
                            "importance": CRITERIA_DEFAULT_WEIGHT,
                            "ignored_criteria": 0,
                        },
                    )
                ],
            ),
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
class PollRecommendationsBaseAPIView(PollScopedViewMixin, ListAPIView):
    """
    A base view used to factorize behaviours common to all recommendation
    views.

    It doesn't define any serializer, queryset nor permission.
    """

    search_score_coef = 2
    _weights_sum = None

    def _metadata_from_filter(self, metadata_filter: str):
        """
        _metadata_from_filter("metadata[language]") -> "language"
        """
        return metadata_filter.split("[")[1][:-1]

    def filter_by_parameters(self, request, queryset, poll: Poll):
        """
        Filter the queryset according to the URL parameters.

        The `unsafe` parameter is not processed by this method.
        """
        filter_serializer = RecommendationsFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        date_lte = filters["date_lte"]
        if date_lte:
            queryset = poll.entity_cls.filter_date_lte(queryset, date_lte)

        date_gte = filters["date_gte"]
        if date_gte:
            queryset = poll.entity_cls.filter_date_gte(queryset, date_gte)

        metadata_filters = [
            (self._metadata_from_filter(key), values)
            for (key, values) in request.query_params.lists()
            if key.startswith("metadata[")
        ]

        if metadata_filters:
            queryset = poll.entity_cls.filter_metadata(queryset, metadata_filters)

        search = filters["search"]
        if search:
            languages = request.query_params.getlist("metadata[language]")
            queryset = poll.entity_cls.filter_search(queryset, search, languages)

        return queryset, filters

    def filter_unsafe(self, queryset, filters):
        """
        Filter the queryset according to the `unsafe` URL parameters.

        This method requires a queryset annotated with the entities weighted
        total score.
        """
        if filters["unsafe"]:
            return queryset

        return queryset.filter(
            rating_n_contributors__gte=settings.RECOMMENDATIONS_MIN_CONTRIBUTORS,
            tournesol_score__gt=0,
        )

    def sort_results(self, queryset, filters):
        """
        Sort the results

        For full-text searches:
        Calculate a "search score" based on the criteria scores and
        the search relevance calculated previously by Postgres.
        There are many possible ways to calculate it, some concerns are:
        - Prefer showing high-rated content
        - A bad but relevant content should have a higher search score
            than a great but totally irrelevant content
        - The search score should always be increasing with the relevance and total score

        This lead to the choice of a model of the type:
            search_score = relevance *
                (relevance + search_score_coef * normalized_total_score)
            where both relevance and normalized_total_score belong to [0, 1].

        With "search_score_coef" an arbitrary, positive value.
            If set to 0, total_score is ignored.
            Set it to a higher value to take more into account the total score.
        """
        if filters["search"] and self.poll_from_url.algorithm == ALGORITHM_MEHESTAN:
            max_absolute_score = MEHESTAN_MAX_SCALED_SCORE * self._weights_sum
            normalized_total_score = (
                (F("total_score") + max_absolute_score) / (2 * max_absolute_score)
            )
            queryset = queryset.alias(
                search_score=F("relevance")
                * (F("relevance") + self.search_score_coef * normalized_total_score)
            )
            return queryset.order_by("-search_score", "-pk")

        return queryset.order_by("-total_score", "-pk")

    def _build_criteria_weight_condition(
        self, request, poll: Poll, when="criteria_scores__criteria"
    ):
        """
        Return a `Case()` expression associating for each criterion the weight
        provided in the URL parameters.
        """
        any_weight_in_request = False
        criteria_cases = []
        weights_sum = 0.0

        for crit in poll.criterias_list:
            weight = self._get_raw_weight(request, crit)
            if weight != CRITERIA_DEFAULT_WEIGHT:
                any_weight_in_request = True
            criteria_cases.append(When(**{when: crit}, then=weight))
            weights_sum += weight

        if not any_weight_in_request and poll.algorithm == ALGORITHM_MEHESTAN:
            criteria_cases = [
                When(**{when: poll.main_criteria}, then=1)
            ]
            weights_sum = 1.0

        self._weights_sum = weights_sum
        return Case(*criteria_cases, default=0)

    def _get_raw_weight(self, request, criteria):
        """Get the weight parameters from the URL"""
        raw_weight = request.query_params.get(f"weights[{criteria}]")
        if raw_weight is None:
            return CRITERIA_DEFAULT_WEIGHT
        try:
            return int(raw_weight)
        except ValueError as value_error:
            raise serializers.ValidationError(
                f"Invalid weight value for criteria '{criteria}'"
            ) from value_error


class PollsView(RetrieveAPIView):
    """
    Fetch a poll and its related criteria.
    """

    permission_classes = []
    queryset = Poll.objects.prefetch_related("criteriarank_set__criteria")
    lookup_field = "name"
    serializer_class = PollSerializer


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "score_mode",
                OpenApiTypes.STR,
                enum=ScoreMode.values,
                default=ScoreMode.DEFAULT,
            ),
        ],
    )
)
class PollsRecommendationsView(PollRecommendationsBaseAPIView):
    """
    List the recommended entities of a given poll sorted by decreasing total
    score.
    """

    # overwrite the default value of `PollScopedViewMixin`
    poll_parameter = "name"

    permission_classes = []

    queryset = Entity.objects.none()
    serializer_class = RecommendationSerializer

    def annotate_and_prefetch_scores(self, queryset, request, poll: Poll):
        raw_score_mode = request.query_params.get("score_mode", ScoreMode.DEFAULT)
        try:
            score_mode = ScoreMode(raw_score_mode)
        except ValueError as error:
            raise serializers.ValidationError(
                {"score_mode": f"Accepted values are: {','.join(ScoreMode.values)}"}
            ) from error

        criteria_weight = self._build_criteria_weight_condition(
            request, poll, when="all_criteria_scores__criteria"
        )
        queryset = queryset.filter(
            all_criteria_scores__poll=poll,
            all_criteria_scores__score_mode=score_mode,
        )

        queryset = queryset.annotate(
            total_score=Sum(
                F("all_criteria_scores__score") * criteria_weight,
            )
        )

        return queryset.filter(total_score__isnull=False).with_prefetched_scores(
            poll_name=poll.name, mode=score_mode
        )

    def get_queryset(self):
        poll = self.poll_from_url
        queryset = Entity.objects.all()
        queryset, filters = self.filter_by_parameters(self.request, queryset, poll)
        queryset = self.annotate_and_prefetch_scores(queryset, self.request, poll)
        queryset = self.filter_unsafe(queryset, filters)
        queryset = self.sort_results(queryset, filters)
        return queryset


class PollsEntityView(PollScopedViewMixin, RetrieveAPIView):
    """
    Fetch an entity with its poll specific statistics.
    """

    poll_parameter = "name"

    permission_classes = []
    queryset = Entity.objects.none()
    serializer_class = RecommendationSerializer

    def get_object(self):
        """Get the entity based on the requested uid."""
        entity_uid = self.kwargs.get("uid")
        entity = get_object_or_404(Entity, uid=entity_uid)

        # The `total_score` is not a natural attribute of an entity. It is
        # used by the recommendations API and computed during the queryset
        # building. The value of the `total_score` may vary depending on the
        # criteria filters used in a recommendations HTTP request. As there is
        # no such filters in the `PollsEntityView` we consider that the
        # `total_score` matches the `tournesol_score`.
        entity.total_score = entity.tournesol_score
        return entity


class PollsCriteriaScoreDistributionView(PollScopedViewMixin, RetrieveAPIView):
    """
    Fetch an entity with the distribution of its contributors' ratings per criteria.
    """

    poll_parameter = "name"

    permission_classes = []
    queryset = Entity.objects.none()
    serializer_class = EntityCriteriaDistributionSerializer

    def get_object(self):
        """Get the entity based on the requested uid."""
        entity_uid = self.kwargs.get("uid")
        return get_object_or_404(Entity, uid=entity_uid)
