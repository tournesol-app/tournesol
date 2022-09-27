from collections import defaultdict
from math import sqrt

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from tournesol.models import ComparisonCriteriaScore, ContributorRatingCriteriaScore
from tournesol.serializers.inconsistencies import (
    Length3CyclesFilterSerializer,
    Length3CyclesSerializer,
    ScoreInconsistenciesFilterSerializer,
    ScoreInconsistenciesSerializer,
)
from tournesol.utils.constants import COMPARISON_MAX
from tournesol.views.mixins.poll import PollScopedViewMixin


@extend_schema_view(
    get=extend_schema(
        parameters=[
            Length3CyclesFilterSerializer,
        ]
    )
)
class Length3Cycles(PollScopedViewMixin, GenericAPIView):
    """
    List the cycles of length 3 in the comparisons graphs.

    These "graphs" (one graph per criteria) are modeled by considering
    entities as nodes, and comparisons as directed edges.

    A cycle between 3 entities A, B, C is when A is preferred to
    B, which is preferred to C, which is preferred to A (A > B > C > A).
    Longer cycles are ignored, because it would be too long to count.

    A "comparison trio" is any set of 3 entities that are all compared to each other.
    The ratio cycles_count / comparison_trios_count can be used as an indicator of consistency.
    """

    serializer_class = Length3CyclesSerializer

    permission_classes = [IsAuthenticated]

    cycles = []
    all_entities = set()
    outgoing_connections = {}
    incoming_connections = {}
    all_connections = {}

    def get(self, request, *args, **kwargs):
        poll = self.poll_from_url
        user = request.user

        stats = {}
        self.cycles = []

        filter_serializer = ScoreInconsistenciesFilterSerializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        filters = filter_serializer.validated_data
        comparisons = ComparisonCriteriaScore.objects.filter(
            comparison__user=user,
            comparison__poll=poll,
        )

        if filters["date_gte"]:
            comparisons = comparisons.filter(
                comparison__datetime_lastedit__gte=filters["date_gte"]
            )

        comparisons = list(
            comparisons.values(
                "comparison__entity_1__uid",
                "comparison__entity_2__uid",
                "criteria",
                "score",
            )
        )

        for criteria in poll.criterias_list:

            self._fill_graph_parameters(comparisons, criteria)

            cycles_count, comparison_trios_count = \
                self._count_cycles_and_comparison_trios(criteria)

            stats[criteria] = {
                "cycles_count": cycles_count,
                "comparison_trios_count": comparison_trios_count,
            }

        response = {
            "count": len(self.cycles),
            "results": self.cycles,
            "stats": stats,
        }

        return Response(Length3CyclesSerializer(response).data)

    def _fill_graph_parameters(self, comparisons: list, criteria):
        """
        Fill the set containing all the entities.

        The incoming and outgoing connections sets are used to search the cycles.
        all_connections is only used to count all the comparison trios.

        outgoing_connections: Dictionary of sets for each entity.
                              Each element in the sets is a preferred entity.
        incoming_connections: Idem but each element in the sets is a worse rated entity.

        all_connections: all the edges (also including comparisons with a score of 0 as edges)
        """
        self.outgoing_connections = defaultdict(set)
        self.incoming_connections = defaultdict(set)
        self.all_connections = defaultdict(set)

        criteria_comparisons = list(
            filter(lambda d: d["criteria"] == criteria, comparisons)
        )

        for comparison in criteria_comparisons:
            entity_1 = comparison["comparison__entity_1__uid"]
            entity_2 = comparison["comparison__entity_2__uid"]

            self.all_connections[entity_1].add(entity_2)
            self.all_connections[entity_2].add(entity_1)

            if comparison["score"] > 0:
                # Entity_2 is preferred
                self.incoming_connections[entity_2].add(entity_1)
                self.outgoing_connections[entity_1].add(entity_2)

            elif comparison["score"] < 0:
                # Entity_1 is preferred
                self.incoming_connections[entity_1].add(entity_2)
                self.outgoing_connections[entity_2].add(entity_1)

    def _count_cycles_and_comparison_trios(self, criteria):
        """
        Count the cycles of length 3 and the comparison trios.
        Add the cycles found to the cycles list.

        The cycles returned are in the order 1, 2, 3 with uid1 < uid2
        and uid1 < uid3, and score_1 > score_2 > score_3 > score_1.
        """
        cycles_count = 0
        comparison_trios_count = 0
        for entity_1 in self.all_connections:
            # Search the cycles
            for entity_2 in self.outgoing_connections[entity_1]:
                # Count only when entity_1 has the lowest uid,to count each cycle only once
                if entity_1 < entity_2:
                    for entity_3 in self.incoming_connections[entity_1] & \
                                    self.outgoing_connections[entity_2]:
                        if entity_1 < entity_3:
                            cycles_count += 1
                            self.cycles.append({
                                "criteria": criteria,
                                "entity_1_uid": entity_1,
                                "entity_2_uid": entity_2,
                                "entity_3_uid": entity_3,
                            })

            # Count the comparison trios
            for entity_2 in self.all_connections[entity_1]:
                comparison_trios_count += len(self.all_connections[entity_1] &
                                              self.all_connections[entity_2])

        # Every comparison trio should have been counted 6 times
        # (any node can be counted in any order, so 1*2*3 = 6 possible permutations)
        comparison_trios_count //= 6

        return cycles_count, comparison_trios_count


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
    def _list_inconsistent_comparisons(  # pylint: disable=too-many-locals
        criteria_comparisons: list,
        criteria_ratings: list,
        threshold: float,
        criteria_list: list
    ) -> dict:
        """
        For each comparison criteria, search the corresponding rating,
        calculate the inconsistency, and check if it crosses the threshold.
        Then prepare the HTTP response.
        """
        comparisons_analysed_count = dict.fromkeys(criteria_list, 0)
        inconsistent_comparisons_count = dict.fromkeys(criteria_list, 0)
        inconsistency_sum = dict.fromkeys(criteria_list, 0.0)

        inconsistent_criteria_comparisons = []

        ratings_map = {
            (rating["contributor_rating__entity__uid"], rating["criteria"]): rating
            for rating in criteria_ratings
        }

        for comparison_criteria in criteria_comparisons:

            entity_1 = comparison_criteria["comparison__entity_1__uid"]
            entity_2 = comparison_criteria["comparison__entity_2__uid"]
            criteria = comparison_criteria["criteria"]
            comparison_score = comparison_criteria["score"]

            try:
                rating_1 = ratings_map[(entity_1, criteria)]
                rating_2 = ratings_map[(entity_2, criteria)]
            except KeyError:
                continue

            uncertainty = rating_1["uncertainty"] + rating_2["uncertainty"]

            inconsistency, ideal_comparison_score = ScoreInconsistencies._calculate_inconsistency(
                rating_1["score"],
                rating_2["score"],
                comparison_score,
                uncertainty,
            )

            comparisons_analysed_count[criteria] += 1
            inconsistency_sum[criteria] += inconsistency

            if inconsistency >= threshold:
                inconsistent_comparisons_count[criteria] += 1

                inconsistent_criteria_comparisons.append(
                    {
                        "inconsistency": inconsistency,
                        "criteria": criteria,
                        "entity_1_uid": entity_1,
                        "entity_2_uid": entity_2,
                        "entity_1_rating": rating_1["score"],
                        "entity_2_rating": rating_2["score"],
                        "comparison_score": comparison_score,
                        "expected_comparison_score": ideal_comparison_score,
                    }
                )

        inconsistent_criteria_comparisons.sort(key=lambda d: d['inconsistency'], reverse=True)

        response = {
            "count": len(inconsistent_criteria_comparisons),
            "results": inconsistent_criteria_comparisons,
            "stats": {},
        }
        for criteria in criteria_list:
            mean_inconsistency = 0.0
            if comparisons_analysed_count[criteria] > 0:
                mean_inconsistency = inconsistency_sum[criteria] / \
                                     comparisons_analysed_count[criteria]

            response["stats"][criteria] = {
                "mean_inconsistency": mean_inconsistency,
                "inconsistent_comparisons_count": inconsistent_comparisons_count[criteria],
                "comparisons_count": comparisons_analysed_count[criteria],
            }

        return response

    @staticmethod
    def _calculate_inconsistency(entity_1_calculated_rating,
                                 entity_2_calculated_rating,
                                 comparison_score,
                                 uncertainty) -> float:
        """
        Calculate the inconsistency between the comparison
        criteria score and the general rating of the entity.

        Let's note R the rating difference (rating2 - rating1),
        r its variable counterpart, U the uncertainty and C the
        comparison (positive if the 2nd entity is preferred).
        Consider this function i:
        i(r) = |C - 10r / sqrt(r² + 1)| (cf issue #671 discussion)
        The inconsistency is the minimum of i(r) for r in [R - U, R + U]

        The function i(r), is either:
        1 - always increasing, if c <= -10 (normally, c is in [-10, 10])
        2 - always decreasing, if c >= 10
        3 - decreasing to 0, then increasing (because it is an absolute value)
        So, the inconsistency is:
           - in case 1: i(R - U)
           - in case 2: i(R + U)
           - in case 3: The value of R for which i(r) = 0 is C / sqrt(100 - C²).
                        The inconsistency is 0 if this value is between [R - U, R + U],
                        otherwise it is respectively i(R - U) or i(R + U) if it is on
                        the left or the right of the interval.

        There is also an imprecision of 0.5 on the comparisons,
        since the comparisons are made on integers (considering that contributors
        have to "mentally round" their preferences to the nearest integer).
        This imprecision is subtracted on the result of the previous calculation.

        Also return the "expected" comparison score (10R / sqrt(R² + 1)). This
        can be used by the frontend to indicate to contributors a range
        of "acceptable" values.
        """

        base_rating_difference = entity_2_calculated_rating - entity_1_calculated_rating

        def inconsistency_calculation(rating_diff):
            return abs(comparison_score - COMPARISON_MAX * rating_diff / sqrt(rating_diff**2 + 1))

        min_rating_difference = base_rating_difference - uncertainty
        max_rating_difference = base_rating_difference + uncertainty

        if comparison_score <= -COMPARISON_MAX:
            min_inconsistency = inconsistency_calculation(min_rating_difference)
        elif comparison_score >= COMPARISON_MAX:
            min_inconsistency = inconsistency_calculation(max_rating_difference)
        else:
            root = comparison_score / sqrt(COMPARISON_MAX ** 2 - comparison_score ** 2)
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

        expected_comparison_score = \
            COMPARISON_MAX * base_rating_difference / sqrt(base_rating_difference**2 + 1)

        return inconsistency, expected_comparison_score
