import numpy as np
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from core.tests.factories.user import UserFactory
from tournesol.tests.factories.comparison import ComparisonCriteriaScoreFactory, ComparisonFactory
from tournesol.tests.factories.entity import EntityFactory
from tournesol.tests.factories.poll import CriteriaRankFactory, PollFactory
from tournesol.views.criteria_correlations import get_linregress


def test_compute_correlation():
    def compute_correlation(scores_1: dict, scores_2: dict):
        return getattr(get_linregress(scores_1, scores_2), 'rvalue', None)
        
    assert compute_correlation({}, {}) == None
    assert compute_correlation({"a": 1}, {"b": 1}) == None
    assert compute_correlation({"a": 1}, {"a": 1}) == None
    assert np.allclose(compute_correlation({"a": 1, "b": 2}, {"a": 1, "b": 2}), 1)
    assert np.allclose(compute_correlation({"a": 1, "b": -2}, {"a": -1, "b": 2}), -1)
    assert np.allclose(compute_correlation({"a": 1, "b": -2, "c": -2, "d": 0}, {"a": -1, "b": 2, "c": 2, "d": 0}), -1)
    assert compute_correlation({"a": 1, "b": 2, "c": 0}, {"a": 3, "b": 3, "c": 1}) < 1
    assert compute_correlation({"a": 1, "b": 2}, {"a": 3, "b": 3}) == 0


def test_compute_slope():
    def compute_slope(scores_1: dict, scores_2: dict):
        return getattr(get_linregress(scores_1, scores_2), 'slope', None)

    assert compute_slope({}, {}) == None
    assert compute_slope({"a": 1}, {"b": 1}) == None
    assert compute_slope({"a": 1}, {"a": 1}) == None
    assert compute_slope({"a": 1, "b": -2}, {"a": -1, "b": 2}) == -1
    assert compute_slope({"a": 1, "b": 2}, {"a": 3, "b": 3}) == 0

    entities="qwertzuiopasdfghjklyxcvbnm"
    assert np.allclose(compute_slope(
        {e: 42 - 2 * i for i, e in enumerate(entities)}, 
        {e: 24 + 3 * i for i, e in enumerate(entities)}, 
    ), -3/2)
    assert np.allclose(compute_slope(
        {e: i for i, e in enumerate(entities)}, 
        {e: 24 + 3 * i for i, e in enumerate(entities)}, 
    ), 3)


class CorrelationAPI(TestCase):

    def setUp(self):
        self.user = UserFactory(username="user_test_correlation")
        self.client = APIClient()

        self.poll = PollFactory()
        criterias = [
            CriteriaRankFactory(criteria__name="hello", poll=self.poll, rank=1),
            CriteriaRankFactory(criteria__name="world", poll=self.poll, rank=2),
            CriteriaRankFactory(criteria__name="!", poll=self.poll, rank=3)
        ]
        self.entities = EntityFactory.create_batch(10)
        self.comparisons = [
            ComparisonFactory(user=self.user, poll=self.poll)
            for entity in self.entities
        ]

    def test_correlations_no_data(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/users/me/criteria_correlations/{self.poll.name}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(" ".join(response_json["criterias"]), "hello world !")
        self.assertEqual(len(response_json["correlations"]), 3)
        self.assertEqual(response_json["correlations"][0], [None, None, None])
        self.assertEqual(len(response_json["slopes"]), 3)
        self.assertEqual(response_json["slopes"][0], [None, None, None])

    def test_correlations_non_authenticated_401(self):
        response = self.client.get(f"/users/me/criteria_correlations/{self.poll.name}/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_correlations_wrong_poll_404(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(f"/users/me/criteria_correlations/this_is_not_a_poll/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_correlation_all_zeros(self):
        self.client.force_authenticate(user=self.user)
        for i, comparison in enumerate(self.comparisons):
            ComparisonCriteriaScoreFactory(
                comparison=comparison,
                criteria="hello",
                score=0,
            )
            ComparisonCriteriaScoreFactory(
                comparison=comparison,
                criteria="world",
                score=0,
            )
        response = self.client.get(f"/users/me/criteria_correlations/{self.poll.name}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["correlations"], [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ])
        self.assertEqual(response_json["slopes"], [
            [None, None, None],
            [None, None, None],
            [None, None, None]
        ])


    def test_correlation_perfect_slope(self):
        self.client.force_authenticate(user=self.user)
        for i, comparison in enumerate(self.comparisons):
            ComparisonCriteriaScoreFactory(
                comparison=comparison,
                criteria="hello",
                score=0.1 * i,
            )
            ComparisonCriteriaScoreFactory(
                comparison=comparison,
                criteria="world",
                score=0.2 * i,
            )
            # this comparison related to another poll should not impact the result
            ComparisonCriteriaScoreFactory(
                comparison__user=self.user,
                criteria="another_criteria",
                score=0.3 * i,
            )

        response = self.client.get(f"/users/me/criteria_correlations/{self.poll.name}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["correlations"], [
            [1, 1, None],
            [1, 1, None],
            [None, None, None]
        ])
        self.assertEqual(response_json["slopes"], [
            [1, 1/2, None],
            [2, 1, None],
            [None, None, None]
        ])


    def test_correlation_with_zeros_on_a_criteria(self):
        self.client.force_authenticate(user=self.user)
        for i, comparison in enumerate(self.comparisons):
            ComparisonCriteriaScoreFactory(
                comparison=comparison,
                criteria="hello",
                score=0.1 * i,
            )
            ComparisonCriteriaScoreFactory(
                comparison=comparison,
                criteria="world",
                score=0,
            )

        response = self.client.get(f"/users/me/criteria_correlations/{self.poll.name}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        response_json = response.json()
        self.assertEqual(response_json["correlations"], [
            [1, None, None],
            [0.0, None, None],
            [None, None, None]
        ])
        self.assertEqual(response_json["slopes"], [
            [1, None, None],
            [0.0, None, None],
            [None, None, None]
        ])
