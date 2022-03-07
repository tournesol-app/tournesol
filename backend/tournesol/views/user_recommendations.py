"""
Overrides the Polls API for recommendations specific to one user
"""
from django.db.models import Case, F, Prefetch, Q, Sum, When
from django.shortcuts import get_object_or_404
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from core.models import User
from tournesol.serializers.poll import RecommendationsFilterSerializer
from tournesol.serializers.user_recommendations import UserRecommendationsSerializer

from ..models import ContributorRatingCriteriaScore, Entity
from ..views import WEIGHTS_PARAMETER, PollsRecommendationsView


class ContributorRecommendations(PollsRecommendationsView):
    """
    Base class for personal and external-user recommendations.
    Redefines some recommendations filter functions for a single user.
    """
    serializer_class = UserRecommendationsSerializer
    user = None  # defined by child class

    def get_scores(self, queryset, request, poll):

        criteria_cases = []
        for crit in poll.criterias_list:
            url_weight = request.query_params.get(f"weights[{crit}]")
            if url_weight is not None:
                try:
                    used_weight = int(url_weight)
                except ValueError as error_value:
                    raise serializers.ValidationError(
                        f"Invalid weight value for criteria '{crit}'"
                    ) from error_value
            else:
                used_weight = 10
            criteria_cases.append(When(contributorvideoratings__criteria_scores__criteria=crit,
                                       then=used_weight))
        criteria_weight = Case(*criteria_cases, default=0)

        queryset = queryset.prefetch_related(
            Prefetch(
                "contributorvideoratings__criteria_scores",
                queryset=ContributorRatingCriteriaScore.objects.filter(
                    contributor_rating__poll=poll, contributor_rating__user=self.user),
            )
        )

        return queryset.annotate(
            total_score=Sum(F("contributorvideoratings__criteria_scores__score")
                            * criteria_weight,),
            filter=Q(contributorvideoratings__poll=poll) &
            Q(contributorvideoratings__user=self.user),
        )

    def filter_unsafe(self, queryset, recommendations_filter):

        show_unsafe = recommendations_filter["unsafe"]
        if not show_unsafe:
            # Ignore RECOMMENDATIONS_MIN_CONTRIBUTORS, only filter on the total score
            queryset = queryset.filter(total_score__gt=0)

        return queryset


@extend_schema_view(
    get=extend_schema(
        description="Retrieve a list of entities filtered and sorted by the logged user's rating",
        parameters=[
            RecommendationsFilterSerializer,
            OpenApiParameter(
                "include_private",
                OpenApiTypes.BOOL,
            ),
            WEIGHTS_PARAMETER,
        ],
    )
)
class PersonalRecommendations(ContributorRecommendations):
    """
    View class to access the user's own recommendations
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        self.user = self.request.user
        self.kwargs["name"] = self.kwargs["poll_name"]  # parent class calls it 'name'

        if self.request.query_params.get("include_private") == "true":
            self.queryset = Entity.objects.filter(
                contributorvideoratings__user=self.user
            )
        else:
            self.queryset = Entity.objects.filter(
                contributorvideoratings__user=self.user,
                contributorvideoratings__is_public=True
            )

        return super().get_queryset()


class ExternalUserRecommendations(ContributorRecommendations):
    """
    View class to access another user's recommendations
    """

    def get_queryset(self):
        self.user = get_object_or_404(User, username=self.kwargs["username"])
        self.kwargs["name"] = self.kwargs["poll_name"]  # parent class calls it 'name'

        self.queryset = Entity.objects.filter(
            contributorvideoratings__user__username=self.user,
            contributorvideoratings__is_public=True
        )

        return super().get_queryset()
