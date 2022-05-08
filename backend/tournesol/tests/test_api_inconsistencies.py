import datetime
from math import sqrt

from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.models import (
    Comparison,
    ComparisonCriteriaScore,
    ContributorRating,
    ContributorRatingCriteriaScore,
    Poll,
)
from tournesol.tests.factories.comparison import ComparisonCriteriaScoreFactory, ComparisonFactory
from tournesol.tests.factories.entity import EntityFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory
from tournesol.tests.factories.ratings import (
    ContributorRatingCriteriaScoreFactory,
    ContributorRatingFactory,
)


class Length3CyclesApiTestCase(TestCase):
    """
    TestCase of the length-3 cycles API.
    """

    def setUp(self):
        """
        entity 1 < entity 2 < entity 3 < entity 4 < entity 1
        entity 3 < entity 1
        entity 2 < entity 4
        => 2 cycles (1, 2, 3) and (1, 2, 4) amongst 4 comparison trios
        """
        self.client = APIClient()

        self.user = UserFactory()
        self.poll = Poll.default_poll()
        self.criterion = self.poll.criterias_list[0]

        self.entity_1 = EntityFactory()
        self.entity_2 = EntityFactory()
        self.entity_3 = EntityFactory()
        self.entity_4 = EntityFactory()
        self.entities = [self.entity_1, self.entity_2, self.entity_3, self.entity_4]

        for index, entity in enumerate(self.entities):
            ComparisonCriteriaScoreFactory(
                comparison__poll=self.poll,
                comparison__user=self.user,
                comparison__entity_1=self.entities[index - 1],
                comparison__entity_2=entity,
                criteria=self.criterion,
                score=1,
            )

        ComparisonCriteriaScoreFactory(
            comparison__poll=self.poll,
            comparison__user=self.user,
            comparison__entity_1=self.entity_3,
            comparison__entity_2=self.entity_1,
            criteria=self.criterion,
            score=1,
        )

        ComparisonCriteriaScoreFactory(
            comparison__poll=self.poll,
            comparison__user=self.user,
            comparison__entity_1=self.entity_2,
            comparison__entity_2=self.entity_4,
            criteria=self.criterion,
            score=1,
        )

        self.setup_cycles_count = 2
        self.setup_comparison_trios_count = 4

        self.url = f"/users/me/inconsistencies/length_3_cycles/{self.poll.name}"

    def test_only_for_authorized_users(self):
        """An anonymous user can't access the score inconsistencies API"""
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_multiple_criteria(self):
        """
        Create cycles for multiple criteria of the same comparison,
        and verify the output format
        """
        self.client.force_authenticate(self.user)

        nb_criteria = len(self.poll.criterias_list)
        self.assertGreater(nb_criteria, 1)
        entities = [EntityFactory() for _ in range(3)]

        for index, entity in enumerate(entities):
            comparison = ComparisonFactory(
                poll=self.poll,
                user=self.user,
                entity_1=entities[index - 1],
                entity_2=entity,
            )

            for criterion in self.poll.criterias_list:
                ComparisonCriteriaScoreFactory(
                    comparison=comparison,
                    criteria=criterion,
                    score=1,
                )

        expected_cycles = {criterion: [{e.uid for e in entities}]
                           for criterion in self.poll.criterias_list}

        expected_cycles[self.criterion].append(
            {self.entity_1.uid, self.entity_2.uid, self.entity_3.uid}
        )
        expected_cycles[self.criterion].append(
            {self.entity_1.uid, self.entity_2.uid, self.entity_4.uid}
        )

        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.setup_cycles_count + nb_criteria)
        self.assertEqual(len(response.data["results"]), self.setup_cycles_count + nb_criteria)

        for criterion in self.poll.criterias_list:
            self.assertIn(criterion, response.data["stats"])
            stat = response.data["stats"][criterion]

            if criterion == self.criterion:
                self.assertEqual(stat["cycles_count"], self.setup_cycles_count + 1)
                self.assertEqual(stat["comparison_trios_count"],
                                 self.setup_comparison_trios_count + 1)
            else:
                self.assertEqual(stat["cycles_count"], 1)
                self.assertEqual(stat["comparison_trios_count"], 1)

            cycles = response.data["results"]
            for cycle in cycles:
                cycle_entities_set = {
                    cycle["entity_1_uid"],
                    cycle["entity_2_uid"],
                    cycle["entity_3_uid"]
                }
                self.assertIn(cycle_entities_set, expected_cycles[cycle["criterion"]])

    def test_no_cycle(self):
        """
        Create comparisons so that there are many
        comparison trios but no cycle.
        """
        self.client.force_authenticate(self.user)

        best_entities = [EntityFactory() for _ in range(3)]
        middle_entities = [EntityFactory() for _ in range(3)]
        worst_entities = [EntityFactory() for _ in range(3)]

        for worse_entities, better_entities in zip(
                [worst_entities, middle_entities, worst_entities],
                [middle_entities, best_entities, best_entities]):
            for entity_1 in worse_entities:
                for entity_2 in better_entities:
                    ComparisonCriteriaScoreFactory(
                        comparison__poll=self.poll,
                        comparison__user=self.user,
                        comparison__entity_1=entity_1,
                        comparison__entity_2=entity_2,
                        criteria=self.criterion,
                        score=1,
                    )

        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.setup_cycles_count)
        self.assertEqual(len(response.data["results"]), self.setup_cycles_count)
        self.assertEqual(response.data["stats"][self.criterion]["cycles_count"],
                         self.setup_cycles_count)
        self.assertEqual(response.data["stats"][self.criterion]["comparison_trios_count"],
                         3**3 + self.setup_comparison_trios_count)

    def test_only_cycles(self):
        """
        Create comparisons so that all the comparison trios are also cycles.
        """
        self.client.force_authenticate(self.user)

        entities = [[EntityFactory() for _ in range(3)] for _ in range(3)]

        for index in range(3):
            for entity_1 in entities[index - 1]:
                for entity_2 in entities[index]:
                    ComparisonCriteriaScoreFactory(
                        comparison__poll=self.poll,
                        comparison__user=self.user,
                        comparison__entity_1=entity_1,
                        comparison__entity_2=entity_2,
                        criteria=self.criterion,
                        score=1,
                    )

        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3**3 + self.setup_cycles_count)
        self.assertEqual(len(response.data["results"]), 3**3 + self.setup_cycles_count)
        self.assertEqual(response.data["stats"][self.criterion]["cycles_count"],
                         3**3 + self.setup_cycles_count)
        self.assertEqual(response.data["stats"][self.criterion]["comparison_trios_count"],
                         3**3 + self.setup_comparison_trios_count)

    def test_date_filter(self):
        """Can use the date filter to ignore old comparisons"""
        self.client.force_authenticate(self.user)

        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

        response = self.client.get(
            self.url + f"?date_gte={yesterday.isoformat()}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], self.setup_cycles_count)

        response = self.client.get(
            self.url + f"?date_gte={tomorrow.isoformat()}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_ignore_other_polls(self):
        """Test that the result is not affected by other polls"""
        self.client.force_authenticate(self.user)

        request_poll = PollWithCriteriasFactory()

        response = self.client.get(
            f"/users/me/inconsistencies/score/{request_poll.name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

    def test_ignore_other_contributors(self):
        """Test that the result is not affected by other contributors' comparisons"""
        request_user = UserFactory()
        self.client.force_authenticate(request_user)

        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)


default_inconsistency_threshold = 5.0

class ScoreInconsistenciesApiTestCase(TestCase):
    """
    TestCase of the Score Inconsistencies API.
    """

    def setUp(self):
        self.client = APIClient()

        self.user = UserFactory()
        self.poll = Poll.default_poll()
        self.criterion = self.poll.criterias_list[0]

        self.url = f"/users/me/inconsistencies/score/{self.poll.name}"

    def _create_comparison_and_rating(self,
                                      rating_score_1=0.0,
                                      rating_score_2=0.0,
                                      uncertainty=0.0,
                                      comparison_score=default_inconsistency_threshold + 1,
                                      criterion=None,
                                      user=None):
        """
        Creates a comparison, and the rating of both entities.
        By default, to simplify, the ratings and uncertainty are set to 0.

        comparison_score is set to (default_threshold + 1) by default, so that, with the
        comparison imprecision, this will by default return an inconsistency
        of (default_threshold + 0.5), and the comparison will be marked inconsistent.
        """
        if not criterion:
            criterion = self.criterion

        if not user:
            user = self.user

        entity_1 = EntityFactory()
        entity_2 = EntityFactory()

        rating_1 = ContributorRatingFactory(user=user, entity=entity_1, poll=self.poll)
        rating_2 = ContributorRatingFactory(user=user, entity=entity_2, poll=self.poll)

        ComparisonCriteriaScoreFactory(
            comparison__poll=self.poll,
            comparison__user=user,
            comparison__entity_1=entity_1,
            comparison__entity_2=entity_2,
            criteria=criterion,
            score=comparison_score,
        )

        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating_1,
            criteria=criterion,
            score=rating_score_1,
            uncertainty=uncertainty,
        )
        ContributorRatingCriteriaScoreFactory(
            contributor_rating=rating_2,
            criteria=criterion,
            score=rating_score_2,
            uncertainty=uncertainty,
        )


    def test_only_for_authorized_users(self):
        """An anonymous user can't access the score inconsistencies API"""
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


    def test_response_format(self):
        """
        Test with an inconsistent comparison for each criterion,
        and verify the API output format.
        """

        self.client.force_authenticate(self.user)

        entity1 = EntityFactory()
        entity2 = EntityFactory()

        rating_1 = ContributorRatingFactory(user=self.user, entity=entity1, poll=self.poll)
        rating_2 = ContributorRatingFactory(user=self.user, entity=entity2, poll=self.poll)

        comparison = ComparisonFactory(
            poll=self.poll,
            user=self.user,
            entity_1=entity1,
            entity_2=entity2,
        )

        comparison_score = default_inconsistency_threshold + 1
        rating_1_score = 0.01
        rating_2_score = 0.02

        nb_criteria = len(self.poll.criterias_list)
        self.assertGreater(nb_criteria, 1)
        for criterion in self.poll.criterias_list:

            ComparisonCriteriaScoreFactory(
                comparison=comparison,
                criteria=criterion,
                score=comparison_score,
            )

            ContributorRatingCriteriaScoreFactory(
                contributor_rating=rating_1,
                criteria=criterion,
                score=rating_1_score,
                uncertainty=0,
            )

            ContributorRatingCriteriaScoreFactory(
                contributor_rating=rating_2,
                criteria=criterion,
                score=rating_2_score,
                uncertainty=0,
            )

        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], nb_criteria)
        self.assertEqual(response.data["count"], len(response.data["results"]))

        for results in response.data["results"]:
            self.assertIn(results["criterion"], self.poll.criterias_list)
            self.assertGreater(results["inconsistency"], default_inconsistency_threshold)
            self.assertEqual(results["entity_1_uid"], entity1.uid)
            self.assertEqual(results["entity_2_uid"], entity2.uid)
            self.assertEqual(results["entity_1_rating"], rating_1_score)
            self.assertEqual(results["entity_2_rating"], rating_2_score)
            self.assertEqual(results["comparison_score"], comparison_score)
            self.assertGreater(results["expected_comparison_score"], 0)
            self.assertLess(results["expected_comparison_score"], 1)

        for criterion in self.poll.criterias_list:
            self.assertIn(criterion, response.data["stats"])
            stat = response.data["stats"][criterion]
            self.assertEqual(stat["mean_inconsistency"],
                             response.data["results"][0]["inconsistency"])
            self.assertEqual(stat["inconsistent_comparisons_count"], 1)
            self.assertEqual(stat["comparisons_count"], 1)


    def test_date_filter(self):
        """Can filter old comparisons"""
        self.client.force_authenticate(self.user)

        self._create_comparison_and_rating()

        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        yesterday = datetime.datetime.now() - datetime.timedelta(days=1)

        response = self.client.get(
            self.url + f"?date_gte={yesterday.isoformat()}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(
            self.url + f"?date_gte={tomorrow.isoformat()}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)


    def test_threshold_filter(self):
        """Can adjust the inconsistency threshold"""
        self.client.force_authenticate(self.user)

        self._create_comparison_and_rating()

        response = self.client.get(
            self.url + f"?inconsistency_threshold={default_inconsistency_threshold}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)

        response = self.client.get(
            self.url + f"?inconsistency_threshold={default_inconsistency_threshold + 1}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)


    def test_uncertainty(self):
        """
        The effect of the uncertainty on the resulting inconsistency is complex,
        but an uncertainty of 0.1 should be enough here to get below the inconsistency threshold.
        """
        self.client.force_authenticate(self.user)

        self._create_comparison_and_rating(uncertainty = 0.1)

        response = self.client.get(
            self.url + f"?inconsistency_threshold={default_inconsistency_threshold}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)

        self._create_comparison_and_rating()

        response = self.client.get(
            self.url + f"?inconsistency_threshold={default_inconsistency_threshold}",
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


    def test_ignore_other_polls(self):
        """Test that the result is not affected by other polls"""
        self.client.force_authenticate(self.user)

        self._create_comparison_and_rating()

        request_poll = PollWithCriteriasFactory()

        response = self.client.get(
            f"/users/me/inconsistencies/score/{request_poll.name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)


    def test_ignore_other_contributors(self):
        """Test that the result is not affected by or contributor's comparisons"""
        self.client.force_authenticate(self.user)

        user = UserFactory()
        self._create_comparison_and_rating(user=user)

        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 0)


    def test_results_order(self):
        """
        Test that the results are sorted by decreasing inconsistency
        """
        self.client.force_authenticate(self.user)
        comparison_scores_list = [1, 10, 3, 5, 7, 3]
        for comparison_score in comparison_scores_list:
            self._create_comparison_and_rating(comparison_score=comparison_score)

        response = self.client.get(self.url + "?inconsistency_threshold=0", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], len(comparison_scores_list))

        inconsistencies_sum = 0
        for index, comparison_score in enumerate(sorted(comparison_scores_list, reverse=True)):
            inconsistency = response.data["results"][index]["inconsistency"]
            inconsistencies_sum += inconsistency
            self.assertAlmostEqual(inconsistency, comparison_score - 0.5)


    def test_results_stats(self):
        """
        Test that the returned statistics
        """
        self.client.force_authenticate(self.user)
        comparison_scores_list = [1, 2, 3, 4, 5, 6, 7, 8, 9]
        expected_inconsistencies_count = 4
        for comparison_score in comparison_scores_list:
            self._create_comparison_and_rating(comparison_score=comparison_score)

        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], expected_inconsistencies_count)

        self.assertIn(self.criterion, response.data["stats"])
        stat = response.data["stats"][self.criterion]
        self.assertAlmostEqual(stat["mean_inconsistency"],
                               (sum(comparison_scores_list) / len(comparison_scores_list)) - 0.5)
        self.assertEqual(stat["inconsistent_comparisons_count"], expected_inconsistencies_count)
        self.assertEqual(stat["comparisons_count"], len(comparison_scores_list))


    def test_inconsistency_good_rating(self):
        """
        Verify the inconsistency for extremely good ratings.
        The rating_difference can, in theory, take any value.
        The inconsistency though should always be in [0,19.5[ with a comparison
        score of 10 or -10, and in [0,9.5[ for a comparison score of 0.

        It is 19.5 and 9.5 instead of 20 and 10 because if the comparison_imprecision
        (comparison are made on integers, so they are implicitly rounded
        to the nearest integer.)
        """
        self.client.force_authenticate(self.user)
        extremely_good_rating = 10000.0

        self._create_comparison_and_rating(comparison_score=10.0,
                                           rating_score_2=extremely_good_rating)

        response = self.client.get(self.url + "?inconsistency_threshold=0", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["inconsistency"], 0)

        self._create_comparison_and_rating(comparison_score=0.0,
                                           rating_score_2=extremely_good_rating)

        response = self.client.get(self.url + "?inconsistency_threshold=0", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        inconsistency = response.data["results"][0]["inconsistency"]
        self.assertAlmostEqual(inconsistency, 9.5, places=4)

        self._create_comparison_and_rating(comparison_score=-10.0,
                                           rating_score_2=extremely_good_rating)

        response = self.client.get(self.url + "?inconsistency_threshold=0", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        inconsistency = response.data["results"][0]["inconsistency"]
        self.assertAlmostEqual(inconsistency, 19.5, places=4)


    def test_inconsistency_bad_rating(self):
        """
        Verify the inconsistency for extremely bad ratings.
        The inconsistency should always be in [0,19.5[ with a comparison
        score of 10 or -10, and in [0,9.5[ for a comparison score of 0.

        It is 19.5 and 9.5 instead of 20 and 10 because if the comparison_imprecision
        (comparison are made on integers, so they are implicitly rounded
        to the nearest integer.)
        """
        self.client.force_authenticate(self.user)
        extremely_bad_rating = -10000.0

        self._create_comparison_and_rating(comparison_score=-10.0,
                                           rating_score_2=extremely_bad_rating)

        response = self.client.get(self.url + "?inconsistency_threshold=0", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["inconsistency"], 0)

        self._create_comparison_and_rating(comparison_score=0.0,
                                           rating_score_2=extremely_bad_rating)

        response = self.client.get(self.url + "?inconsistency_threshold=0", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 2)
        inconsistency = response.data["results"][0]["inconsistency"]
        self.assertAlmostEqual(inconsistency, 9.5, places=4)

        self._create_comparison_and_rating(comparison_score=10.0,
                                           rating_score_2=extremely_bad_rating)

        response = self.client.get(self.url + "?inconsistency_threshold=0", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 3)
        inconsistency = response.data["results"][0]["inconsistency"]
        self.assertAlmostEqual(inconsistency, 19.5, places=4)


    def test_inconsistency_zero(self):
        """
        The inconsistency 0 can is obtained notably when
        rating_difference = comparison_score / sqrt(100 - comparison_score²)
        (with rating_difference = rating_2 - rating_1)
        """
        self.client.force_authenticate(self.user)

        comparison_score = -6
        rating_difference = comparison_score / sqrt(100 - comparison_score**2)
        self._create_comparison_and_rating(comparison_score=comparison_score,
                                          rating_score_2=rating_difference)

        response = self.client.get(self.url + "?inconsistency_threshold=0", format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(response.data["results"][0]["inconsistency"], 0)

