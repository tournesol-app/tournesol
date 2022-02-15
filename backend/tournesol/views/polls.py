import logging

from django.conf import settings
from django.db.models import Case, F, Prefetch, Q, Sum, When
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

from tournesol.models import Entity, EntityCriteriaScore, Poll
from tournesol.serializers.poll import (
    PollSerializer,
    RecommendationSerializer,
    RecommendationsFilterSerializer,
)

logger = logging.getLogger(__name__)


class PollsView(RetrieveAPIView):
    """
    Retrieve a poll and its related criteria.
    """

    permission_classes = []
    queryset = Poll.objects.prefetch_related("criteriarank_set__criteria")
    lookup_field = "name"
    serializer_class = PollSerializer


@extend_schema_view(
    get=extend_schema(
        description="Retrieve a list of recommended videos, sorted by decreasing total score.",
        parameters=[
            RecommendationsFilterSerializer,
            OpenApiParameter(
                "weights",
                OpenApiTypes.OBJECT,
                style="deepObject",
                description="Weights for criterias in this poll."
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
        ],
    )
)
class PollsRecommendationsView(ListAPIView):
    permission_classes = []
    serializer_class = RecommendationSerializer
    queryset = Entity.objects.none()

    def get_queryset(self):
        request = self.request
        poll = get_object_or_404(Poll, name=self.kwargs["name"])
        criterias = poll.criterias_list

        queryset = Entity.objects.all()

        filter_serializer = RecommendationsFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        recommendations_filter = filter_serializer.validated_data

        search = recommendations_filter["search"]
        if search:
            queryset = poll.entity_cls.filter_search(queryset, search)

        date_lte = recommendations_filter["date_lte"]
        if date_lte:
            queryset = poll.entity_cls.filter_date_lte(queryset, date_lte)

        date_gte = recommendations_filter["date_gte"]
        if date_gte:
            queryset = poll.entity_cls.filter_date_gte(queryset, date_gte)

        criteria_cases = []
        for crit in criterias:
            raw_weight = request.query_params.get(f"weights[{crit}]")
            if raw_weight is not None:
                try:
                    weight = int(raw_weight)
                except ValueError:
                    raise serializers.ValidationError(
                        f"Invalid weight value for criteria '{crit}'"
                    )
            else:
                weight = 10
            criteria_cases.append(When(criteria_scores__criteria=crit, then=weight))
        criteria_weight = Case(*criteria_cases, default=0)

        queryset = queryset.annotate(
            total_score=Sum(
                F("criteria_scores__score") * criteria_weight,
                filter=Q(criteria_scores__poll=poll),
            )
        )

        show_unsafe = recommendations_filter["unsafe"]
        if show_unsafe:
            queryset = queryset.filter(total_score__isnull=False)
        else:
            queryset = queryset.filter(
                rating_n_contributors__gte=settings.RECOMMENDATIONS_MIN_CONTRIBUTORS
            ).filter(total_score__gt=0)

        return queryset.prefetch_related(
            Prefetch(
                "criteria_scores",
                queryset=EntityCriteriaScore.objects.filter(poll=poll),
            )
        ).order_by("-total_score", "-pk")
