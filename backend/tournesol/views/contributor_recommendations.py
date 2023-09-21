"""
Overrides the Polls API for recommendations specific to one user
"""
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from core.models import User
from tournesol.serializers.contributor_recommendations import ContributorRecommendationsSerializer

from ..models import Entity, Poll
from ..views import PollRecommendationsBaseAPIView


class ContributorRecommendationsBaseView(PollRecommendationsBaseAPIView):
    """
    A base class used to factorize behaviours common to all contributor
    recommendations views.
    """

    queryset = Entity.objects.none()
    serializer_class = ContributorRecommendationsSerializer

    def annotate_with_total_score(self, queryset, request, poll: Poll):
        criteria_weight = self._build_criteria_weight_condition(
            request, poll, when="contributorvideoratings__criteria_scores__criteria"
        )
        return queryset.annotate(
            total_score=Sum(
                F("contributorvideoratings__criteria_scores__score") * criteria_weight,
            ),
        ).filter(total_score__isnull=False)


class PrivateContributorRecommendationsView(ContributorRecommendationsBaseView):
    """
    List the recommendations of the logged user sorted by decreasing total
    score.
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        poll = self.poll_from_url
        user = self.request.user

        queryset = (
            Entity.objects.filter(
                contributorvideoratings__poll=poll,
                contributorvideoratings__user=user
            )
            .with_prefetched_scores(poll_name=poll.name)
            .with_prefetched_poll_ratings(poll_name=poll.name)
            .with_prefetched_contributor_ratings(
                poll=poll,
                user=user,
                prefetch_criteria_scores=True
            )
        )

        queryset, filters = self.filter_by_parameters(self.request, queryset, poll)
        queryset = self.annotate_with_total_score(queryset, self.request, poll)
        queryset = self.sort_results(queryset, filters)
        return queryset


class PublicContributorRecommendationsView(ContributorRecommendationsBaseView):
    """
    List the public recommendations of a given user sorted by decreasing total
    score.
    """

    permission_classes = []

    def get_queryset(self):
        poll = self.poll_from_url
        user = get_object_or_404(User, username=self.kwargs["username"], is_active=True)

        queryset = (
            Entity.objects.filter(
                contributorvideoratings__poll=poll,
                contributorvideoratings__user=user,
                contributorvideoratings__is_public=True,
            )
            .with_prefetched_scores(poll_name=poll.name)
            .with_prefetched_poll_ratings(poll_name=poll.name)
            .with_prefetched_contributor_ratings(
                poll=poll,
                user=user,
                prefetch_criteria_scores=True
            )
        )

        queryset, filters = self.filter_by_parameters(self.request, queryset, poll)
        queryset = self.annotate_with_total_score(queryset, self.request, poll)
        queryset = self.sort_results(queryset, filters)
        return queryset
