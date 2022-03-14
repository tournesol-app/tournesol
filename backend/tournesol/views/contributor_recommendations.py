"""
Overrides the Polls API for recommendations specific to one user
"""
from django.db.models import Case, F, Prefetch, Sum, When
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated

from core.models import User
from tournesol.serializers.contributor_recommendations import ContributorRecommendationsSerializer

from ..models import ContributorRating, Entity, Poll
from ..views import PollRecommendationsBaseAPIView


class ContributorRecommendationsBaseView(PollRecommendationsBaseAPIView):
    """
    A base class used to factorize behaviours common to all contributor
    recommendations views.
    """

    queryset = Entity.objects.none()
    serializer_class = ContributorRecommendationsSerializer

    def annotate_with_total_score(self, queryset, request, poll: Poll, user):
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
            criteria_cases.append(
                When(
                    contributorvideoratings__criteria_scores__criteria=crit,
                    then=used_weight,
                )
            )
        criteria_weight = Case(*criteria_cases, default=0)

        queryset = queryset.prefetch_related(
            Prefetch(
                "contributorvideoratings",
                queryset=ContributorRating.objects.filter(poll=poll, user=user),
            ),
            "contributorvideoratings__criteria_scores",
        )

        return queryset.filter(
            contributorvideoratings__user=user, contributorvideoratings__poll=poll
        ).annotate(
            total_score=Sum(
                F("contributorvideoratings__criteria_scores__score") * criteria_weight,
            ),
        )

    def filter_unsafe(self, queryset, filters):
        show_unsafe = filters["unsafe"]
        if not show_unsafe:
            # Ignore RECOMMENDATIONS_MIN_CONTRIBUTORS, only filter on the
            # total score
            queryset = queryset.filter(total_score__gt=0)

        return queryset.distinct()


class PrivateContributorRecommendationsView(ContributorRecommendationsBaseView):
    """
    List the recommendations of the logged user sorted by decreasing total
    score.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        poll = self.poll_from_url
        user = self.request.user

        queryset = Entity.objects.filter(contributorvideoratings__user=user)

        queryset, filters = self.filter_by_parameters(self.request, queryset, poll)
        queryset = self.annotate_with_total_score(queryset, self.request, poll, user)
        queryset = self.filter_unsafe(queryset, filters)
        return queryset.order_by("-total_score", "-pk")


class PublicContributorRecommendationsView(ContributorRecommendationsBaseView):
    """
    List the public recommendations of a given user sorted by decreasing total
    score.
    """

    permission_classes = []

    def get_queryset(self):
        poll = self.poll_from_url
        user = get_object_or_404(User, username=self.kwargs["username"])

        queryset = Entity.objects.filter(
            contributorvideoratings__user=user, contributorvideoratings__is_public=True
        )

        queryset, filters = self.filter_by_parameters(self.request, queryset, poll)
        queryset = self.annotate_with_total_score(queryset, self.request, poll, user)
        queryset = self.filter_unsafe(queryset, filters)
        return queryset.order_by("-total_score", "-pk")
