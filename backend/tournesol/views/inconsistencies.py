from math import sqrt

from django.db.models import ObjectDoesNotExist
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tournesol.models import ComparisonCriteriaScore, ContributorRatingCriteriaScore
from tournesol.serializers.inconsistencies import (
    ScoreInconsistenciesFilterSerializer,
    ScoreInconsistenciesSerializer,
)
from tournesol.views.mixins.poll import PollScopedViewMixin


@extend_schema_view(
    get=extend_schema(
        parameters=[
            ScoreInconsistenciesFilterSerializer,
        ]
    )
)
class ScoreInconsistencies(PollScopedViewMixin, GenericAPIView):
    """
    List the comparisons criteria for which the given score is very
    different from what would be expected from both entities' criteria scores.
    """

    serializer_class = ScoreInconsistenciesSerializer

    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        poll = self.poll_from_url
        user = request.user

        filter_serializer = ScoreInconsistenciesFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data

        contributor_comparisons_criteria = ComparisonCriteriaScore.objects.filter(
            comparison__user=user,
            comparison__poll=poll,
        ).select_related("comparison")

        if filters["date_gte"]:
            contributor_comparisons_criteria = contributor_comparisons_criteria.filter(
                comparison__datetime_lastedit__gte=filters["date_gte"]
            )

        ratings = ContributorRatingCriteriaScore.objects.filter(
            contributor_rating__user=user,
            contributor_rating__poll=poll,
        ).select_related("contributor_rating")

        comparisons_count = 0
        inconsistency_sum = 0.0
        inconsistencies_count = 0
        inconsistent_criterion_comparisons = []

        for comparison_criterion in contributor_comparisons_criteria:
            comparisons_count += 1

            entity_1 = comparison_criterion.comparison.entity_1
            entity_2 = comparison_criterion.comparison.entity_2

            try:
                entity_1_rating = ratings.get(
                    contributor_rating__entity=entity_1,
                    criteria=comparison_criterion.criteria,
                )
                entity_2_rating = ratings.get(
                    contributor_rating__entity=entity_2,
                    criteria=comparison_criterion.criteria,
                )
            except ObjectDoesNotExist:
                continue

            uncertainty = entity_1_rating.uncertainty + entity_2_rating.uncertainty

            inconsistency = self._calculate_inconsistency(entity_1_rating.score,
                                                          entity_2_rating.score,
                                                          comparison_criterion.score,
                                                          uncertainty)

            if inconsistency >= filters["inconsistency_threshold"]:
                inconsistencies_count += 1
                inconsistency_sum += inconsistency
                criterion_comparison = {
                    "inconsistency": inconsistency,
                    "entity_1_uid": entity_1,
                    "entity_2_uid": entity_2,
                    "criteria": comparison_criterion.criteria,
                    "comparison_score": comparison_criterion.score,
                    "entity_1_rating": entity_1_rating.score,
                    "entity_2_rating": entity_2_rating.score,
                }
                inconsistent_criterion_comparisons.append(criterion_comparison)

        inconsistent_criterion_comparisons.sort(key=lambda d: d['inconsistency'], reverse=True)

        # No need to return everything, return at most 100 elements
        inconsistent_criterion_comparisons = inconsistent_criterion_comparisons[:100]

        mean_inconsistency = 0
        if comparisons_count > 0:
            mean_inconsistency = inconsistency_sum / comparisons_count

        response = {
            "mean_inconsistency": mean_inconsistency,
            "count": len(inconsistent_criterion_comparisons),
            "results": inconsistent_criterion_comparisons,
        }

        return Response(ScoreInconsistenciesSerializer(response).data)

    @staticmethod
    def _calculate_inconsistency(entity_1_calculated_rating,
                                 entity_2_calculated_rating,
                                 comparison_score,
                                 uncertainty):
        """
        Calculate the inconsistency between the comparison
        criterion score and the general rating of the entity.

        Let's note R the rating difference (rating2 - rating1),
        r its variable counterpart, U the uncertainty and C the
        comparison (positive if the 2nd entity is preferred).
        Consider this function i:
        i(r) = |C - 10r / sqrt(r² + 1)| (cf issue #671 discussion)
        The inconsistency is the minimum of i(r) for r in [R - U, R + U]

        The function i(r), is either:
        1 - always increasing, if c <= -10 (normally, c is in [-10, 10])
        2 - decreasing to 0, then increasing (because it is an absolute value)
        3 - always decreasing, if c >= 10
        So, the inconsistency is either i(R - U) in case 1, inconsistency(R + U)
        in case 3, or 0 in case 2.
        The value of R for which i(r) = 0 is C / sqrt(100 - C²), which
        helps in case 2 to know if the minimum is 0 by checking if this root
        is in [R - U, R + U].

        There is also an imprecision of 0.5 on the comparison,
        since the comparisons are made on floats and not integers,
        which is subtracted on the result of the previous calculation.
        """

        base_rating_difference = entity_2_calculated_rating - entity_1_calculated_rating

        def inconsistency_calculation(rating_difference):
            return abs(comparison_score - 10 * rating_difference /
                       sqrt((rating_difference**2) + 1))

        min_rating_difference = base_rating_difference - uncertainty
        max_rating_difference = base_rating_difference + uncertainty

        if comparison_score <= -10:
            min_inconsistency = inconsistency_calculation(min_rating_difference)
        elif comparison_score >= 10:
            min_inconsistency = inconsistency_calculation(max_rating_difference)
        else:
            root = comparison_score / sqrt(100 - comparison_score**2)
            if max_rating_difference < root:
                # The inconsistency is decreasing with the rating_difference
                min_inconsistency = inconsistency_calculation(max_rating_difference)
            elif root < min_rating_difference:
                # The inconsistency is increasing with the rating_difference
                min_inconsistency = inconsistency_calculation(min_rating_difference)
            else:
                # The root is a possible value for the rating_difference
                min_inconsistency = 0

        # Comparison imprecision of 0.5, because comparisons scores are on integers, not floats
        inconsistency = max(min_inconsistency - 0.5, 0)

        return inconsistency
