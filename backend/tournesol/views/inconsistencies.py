from math import sqrt

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
        )

        if filters["date_gte"]:
            contributor_comparisons_criteria = contributor_comparisons_criteria.filter(
                comparison__datetime_lastedit__gte=filters["date_gte"]
            )
        contributor_comparisons_criteria = list(
            contributor_comparisons_criteria.values(
                "comparison__entity_1__uid",
                "comparison__entity_2__uid",
                "criteria",
                "score",
            )
        )

        ratings = list(
            ContributorRatingCriteriaScore.objects.filter(
                contributor_rating__user=user,
                contributor_rating__poll=poll,
            ).values(
                "contributor_rating__entity__uid",
                "criteria",
                "uncertainty",
                "score",
            )
        )

        response = self._list_inconsistent_comparisons(contributor_comparisons_criteria,
                                                       ratings,
                                                       filters["inconsistency_threshold"],
                                                       poll.criterias_list)

        return Response(ScoreInconsistenciesSerializer(response).data)

    @staticmethod
    def _list_inconsistent_comparisons(criteria_comparisons: list,
                                       criteria_ratings: list,
                                       threshold: float,
                                       criteria_list: list) -> dict:
        """
        For each comparison criterion, search the corresponding rating,
        calculate the inconsistency, and check if it crosses the threshold.
        Then prepare the HTTP response.
        """
        response = {}

        comparisons_analysed_count = dict.fromkeys(criteria_list, 0)
        inconsistent_comparisons_count = dict.fromkeys(criteria_list, 0)
        inconsistency_sum = dict.fromkeys(criteria_list, 0.0)
        mean_inconsistency = dict.fromkeys(criteria_list, 0.0)

        inconsistent_criterion_comparisons = []

        ratings_map = {
            (rating["contributor_rating__entity__uid"], rating["criteria"]): rating
            for rating in criteria_ratings
        }

        for comparison_criterion in criteria_comparisons:

            entity_1 = comparison_criterion["comparison__entity_1__uid"]
            entity_2 = comparison_criterion["comparison__entity_2__uid"]
            criterion = comparison_criterion["criteria"]
            comparison_score = comparison_criterion["score"]

            try:
                rating_1 = ratings_map[(entity_1, criterion)]
                rating_2 = ratings_map[(entity_2, criterion)]
            except KeyError:
                continue

            uncertainty = rating_1["uncertainty"] + rating_2["uncertainty"]

            inconsistency = ScoreInconsistencies._calculate_inconsistency(rating_1["score"],
                                                                          rating_2["score"],
                                                                          comparison_score,
                                                                          uncertainty)

            comparisons_analysed_count[criterion] += 1
            inconsistency_sum[criterion] += inconsistency
            mean_inconsistency[criterion] = inconsistency_sum[criterion] / \
                comparisons_analysed_count[criterion]

            if inconsistency >= threshold:
                inconsistent_comparisons_count[criterion] += 1

                inconsistent_criterion_comparisons.append(
                    {
                        "inconsistency": inconsistency,
                        "criterion": criterion,
                        "entity_1_uid": entity_1,
                        "entity_2_uid": entity_2,
                        "comparison_score": comparison_score,
                        "entity_1_rating": rating_1["score"],
                        "entity_2_rating": rating_2["score"],
                    }
                )

        inconsistent_criterion_comparisons.sort(key=lambda d: d['inconsistency'], reverse=True)

        response["count"] = len(inconsistent_criterion_comparisons)
        response["results"] = inconsistent_criterion_comparisons
        response["stats"] = {}
        for criterion in criteria_list:
            response["stats"][criterion] = {
                "mean_inconsistency": mean_inconsistency[criterion],
                "inconsistent_comparisons_count": inconsistent_comparisons_count[criterion],
                "comparisons_count": comparisons_analysed_count[criterion],
            }

        return response

    @staticmethod
    def _calculate_inconsistency(entity_1_calculated_rating,
                                 entity_2_calculated_rating,
                                 comparison_score,
                                 uncertainty) -> float:
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

        There is also an imprecision of 0.5 on the comparisons,
        since the comparisons are made on integers (considering that contributors
        have to "mentally round" their preferences to the nearest integer).
        This imprecision is subtracted on the result of the previous calculation.
        """

        base_rating_difference = entity_2_calculated_rating - entity_1_calculated_rating
        comparison_max = 10

        def inconsistency_calculation(rating_diff):
            return abs(comparison_score - comparison_max * rating_diff / sqrt(rating_diff**2 + 1))

        min_rating_difference = base_rating_difference - uncertainty
        max_rating_difference = base_rating_difference + uncertainty

        if comparison_score <= -comparison_max:
            min_inconsistency = inconsistency_calculation(min_rating_difference)
        elif comparison_score >= comparison_max:
            min_inconsistency = inconsistency_calculation(max_rating_difference)
        else:
            root = comparison_score / sqrt(comparison_max**2 - comparison_score**2)
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
