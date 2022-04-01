from django.http import JsonResponse
from drf_spectacular.utils import extend_schema
from rest_framework import serializers
from rest_framework.generics import GenericAPIView
from scipy.stats import linregress

from tournesol.models.ratings import ContributorRating
from tournesol.views.mixins.poll import PollScopedViewMixin


def get_linregress(scores_1: dict, scores_2: dict):
    """
    inputs are dictionaries with entities as keys and scores as values
    for a given user and a given rating criteria
    """
    # At least two datapoints are necessary to compute the slope and correlation
    if sum(entity in scores_1 for entity in scores_2) > 1:
        try:
            return linregress(
                [scores_1[e] for e in scores_1 if e in scores_2],
                [scores_2[e] for e in scores_1 if e in scores_2],
            )
        except ValueError:
            # regression is undefined if all x values are identical
            # (e.g all scores are 0 for one of the criteria)
            return None
    else:
        return None


class ContributorCriteriaCorrelationsSerializer(serializers.Serializer):
    criterias = serializers.ListField(child=serializers.CharField())
    correlations = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField())
    )
    slopes = serializers.ListField(
        child=serializers.ListField(child=serializers.FloatField())
    )


class ContributorCriteriaCorrelationsView(PollScopedViewMixin, GenericAPIView):

    @extend_schema(
        responses={
            200: ContributorCriteriaCorrelationsSerializer
        }
    )
    def get(self, request, **kwargs):
        """
        Retrieves the correlation between each pair of criteria
        of the logged user and the given poll.
        """
        criterias = self.poll_from_url.criterias_list

        ratings = ContributorRating.objects.prefetch_related("criteria_scores").filter(
            poll=self.poll_from_url,
            user=request.user
        )

        scores = {criteria: {} for criteria in criterias}
        for r in ratings:
            for s in r.criteria_scores.all():
                scores[s.criteria][r.entity] = s.score

        linear_regressions = {
            c1: {c2: get_linregress(scores[c1], scores[c2]) for c2 in criterias}
            for c1 in criterias
        }
        serializer = ContributorCriteriaCorrelationsSerializer({
            "criterias": criterias,
            "correlations": [
                [getattr(linear_regressions[c1][c2], 'rvalue', None) for c1 in criterias]
                for c2 in criterias
            ],
            "slopes": [
                [getattr(linear_regressions[c1][c2], 'slope', None) for c1 in criterias]
                for c2 in criterias
            ],
        })

        return JsonResponse(serializer.data)
