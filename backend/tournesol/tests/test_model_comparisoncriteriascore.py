"""
All test cases of the `ComparisonCriteriaScore` model.
"""

from django.db import IntegrityError, transaction
from django.test import TestCase

from core.tests.factories.user import UserFactory
from tournesol.models import ComparisonCriteriaScore
from tournesol.tests.factories.comparison import ComparisonFactory
from tournesol.tests.factories.poll import PollWithCriteriasFactory


class ComparisonCriteriaScoreTestCase(TestCase):
    """
    TestCase of the `ComparisonCriteriaScore` model.
    """

    _user = "username"

    def setUp(self):
        self.poll = PollWithCriteriasFactory()
        self.user = UserFactory(username=self._user)
        self.comparison = ComparisonFactory(
            user=self.user,
            poll=self.poll,
        )

    def test_save_validate_score(self):
        score = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=11,
            score_magnitude=10,
        )

        # The score cannot be superior to the magnitude.
        with self.assertRaises(ValueError):
            score.save()

        score.score = -11
        # The absolute value of the score cannot be superior to the magnitude.
        with self.assertRaises(ValueError):
            score.save()

        # The score can be equal to the magnitude.
        score.score = score.score_magnitude
        score.save()

        # The absolute value of the score can be inferior to the magnitude.
        score.score = 0
        score.save()
