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
from tournesol.serializers.entity import EntityCriteriaDistributionSerializer
from tournesol.serializers.poll import (
    PollSerializer,
    RecommendationSerializer,
    RecommendationsFilterSerializer,
)
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
                " The default weight is 10 for each criteria.",
                examples=[
                    OpenApiExample(
                        name="weights example",
                        value={
                            "reliability": 10,
                            "importance": 10,
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
                        name="Some filters available for videos.",
                        value={"language": "fr,pt", "uploader": "kurzgesagtES"},
                    ),
                    OpenApiExample(
                        name="Some filters available for candidates.",
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

    def _metadata_from_filter(self, filtr: str):
        """
        _metadata_from_filter("metadata[language]") -> "language"
        """
        return filtr.split("[")[1][:-1]

    def filter_by_parameters(self, request, queryset, poll: Poll):
        """
        Filter the queryset according to the URL parameters.

        The `unsafe` parameter is not processed by this method.
        """
        filter_serializer = RecommendationsFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        search = filters["search"]
        if search:
            queryset = poll.entity_cls.filter_search(queryset, search)

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

        return queryset, filters

    def filter_unsafe(self, queryset, filters):
        """Filter the queryset according to the `unsafe` URL parameters.

        This method requires a queryset annotated with the entities weighted
        total score.
        """
        show_unsafe = filters["unsafe"]
        if show_unsafe:
            queryset = queryset.filter(total_score__isnull=False)
        else:
            queryset = queryset.filter(
                rating_n_contributors__gte=settings.RECOMMENDATIONS_MIN_CONTRIBUTORS
            ).filter(total_score__gt=0)

        return queryset

    def _build_criteria_weight_condition(
        self, request, poll: Poll, when="criteria_scores__criteria"
    ):
        """
        Return a `Case()` expression associating for each criterion the weight
        provided in the URL parameters.
        """
        criteria_cases = []
        for crit in poll.criterias_list:
            raw_weight = request.query_params.get(f"weights[{crit}]")
            if raw_weight is not None:
                try:
                    weight = int(raw_weight)
                except ValueError as value_error:
                    raise serializers.ValidationError(
                        f"Invalid weight value for criteria '{crit}'"
                    ) from value_error
            else:
                weight = 10
            criteria_cases.append(When(**{when: crit}, then=weight))
        return Case(*criteria_cases, default=0)


class PollsView(RetrieveAPIView):
    """
    Fetch a poll and its related criteria.
    """

    permission_classes = []
    queryset = Poll.objects.prefetch_related("criteriarank_set__criteria")
    lookup_field = "name"
    serializer_class = PollSerializer


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

    def annotate_with_total_score(self, queryset, request, poll: Poll):
        score_mode = ScoreMode.DEFAULT
        criteria_weight = self._build_criteria_weight_condition(
            request, poll, when="all_criteria_scores__criteria"
        )
        queryset = (
            queryset
            .filter(all_criteria_scores__score_mode=score_mode)
            .annotate(
                total_score=Sum(
                    F("all_criteria_scores__score") * criteria_weight,
                )
            )
        )
        return queryset.with_prefetched_scores(poll_name=poll.name, mode=score_mode)

    def get_queryset(self):
        poll = self.poll_from_url
        queryset = Entity.objects.filter(all_criteria_scores__poll=poll)
        queryset, filters = self.filter_by_parameters(self.request, queryset, poll)
        queryset = self.annotate_with_total_score(queryset, self.request, poll)
        queryset = self.filter_unsafe(queryset, filters)
        return queryset.order_by("-total_score", "-pk")


class PollsCriteriaScoreDistributionView(PollScopedViewMixin, RetrieveAPIView):
    """
    Get the distribution of the contributor's ratings per criteria for an entity
    """

    poll_parameter = "name"

    permission_classes = []
    queryset = Entity.objects.none()
    serializer_class = EntityCriteriaDistributionSerializer

    def get_object(self):
        """ Get object based on the entity uid """
        entity_uid = self.kwargs.get("uid")
        return get_object_or_404(Entity, uid=entity_uid)
