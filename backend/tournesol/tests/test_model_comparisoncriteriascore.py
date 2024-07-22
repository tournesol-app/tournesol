"""
All test cases of the `ComparisonCriteriaScore` model.
"""

from django.core.exceptions import ValidationError
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
        self.comparison = ComparisonFactory(poll=self.poll, user=self.user)

    def test_validators_score_max(self):
        score = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=0,
            score_max=0,
        )

        # score_max cannot be zero.
        with self.assertRaises(ValidationError):
            score.clean_fields()

        score.score_max = -1
        # score_max cannot be negative.
        with self.assertRaises(ValidationError):
            score.clean_fields()

        score.score_max = 1
        score.clean_fields()

    def test_method_validate_score_max(self):
        score_test = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=11,
            score_max=10,
        )

        # The score cannot be greater than score_max.
        with self.assertRaises(ValueError):
            score_test._validate_score_max()

        score_test.score = -11
        # The absolute value of the score cannot be greater than score_max.
        with self.assertRaises(ValueError):
            score_test._validate_score_max()

        # The score can be zero.
        score_test.score = 0
        score_test._validate_score_max()

        # The score can be equal to the score_max.
        score_test.score = score_test.score_max
        score_test._validate_score_max()

        # The absolute value of the score can be lesser than score_max.
        score_test.score = -1
        score_test._validate_score_max()

        score_max_test = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=5,
            score_max=None,
        )

        # score_max cannot be None.
        with self.assertRaises(TypeError):
            score_max_test._validate_score_max()

        score_max_test.score_max = 0
        # score_max cannot be zero.
        with self.assertRaises(ValueError):
            score_max_test._validate_score_max()

        score_max_test.score_max = -10
        # score_max cannot be negative.
        with self.assertRaises(ValueError):
            score_max_test._validate_score_max()

        score_max_test.score_max = 10
        score_max_test._validate_score_max()

    def test_method_clean_calls_validate_score_max(self):
        score_test = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=11,
            score_max=10,
        )

        # The score cannot be greater than score_max.
        with self.assertRaises(ValidationError):
            score_test.clean()

        score_test.score = -11
        # The absolute value of the score cannot be greater than score_max.
        with self.assertRaises(ValidationError):
            score_test.clean()

        # The score can be zero.
        score_test.score = 0
        score_test.clean()

        # The score can be equal to the score_max.
        score_test.score = score_test.score_max
        score_test.clean()

        # The absolute value of the score can be lesser than score_max.
        score_test.score = -1
        score_test.clean()

        score_max_test = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=5,
            score_max=None,
        )

        # score_max cannot be None.
        with self.assertRaises(ValidationError):
            score_max_test.clean()

        score_max_test.score_max = 0
        # score_max cannot be zero.
        with self.assertRaises(ValidationError):
            score_max_test.clean()

        score_max_test.score_max = -10
        # score_max cannot be negative.
        with self.assertRaises(ValidationError):
            score_max_test.clean()

        score_max_test.score_max = 10
        score_max_test.clean()

    def test_method_save_calls_validate_score_max(self):
        score_test = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=11,
            score_max=10,
        )

        # The score cannot be greater than score_max.
        with self.assertRaises(ValueError):
            score_test.save()

        score_test.score = -11
        # The absolute value of the score cannot be greater than score_max.
        with self.assertRaises(ValueError):
            score_test.save()

        # The score can be zero.
        score_test.score = 0
        score_test.save()

        # The score can be equal to the score_max.
        score_test.score = score_test.score_max
        score_test.save()

        # The absolute value of the score can be lesser than score_max.
        score_test.score = -1
        score_test.save()
        score_test.delete()

        score_max_test = ComparisonCriteriaScore(
            comparison=self.comparison,
            criteria=self.poll.main_criteria,
            score=5,
            score_max=None,
        )

        # score_max cannot be None.
        with self.assertRaises(TypeError):
            score_max_test.save()

        score_max_test.score_max = 0
        # score_max cannot be zero.
        with self.assertRaises(ValueError):
            score_max_test.save()

        score_max_test.score_max = -10
        # score_max cannot be negative.
        with self.assertRaises(ValueError):
            score_max_test.save()

        score_max_test.score_max = 10
        score_max_test.save()
